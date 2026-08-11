"""
ArXiv Daily Tracker - 主入口编排脚本。

用法:
    python scripts/main.py                  # 运行全部任务
    python scripts/main.py --task arxiv     # 仅运行 ArXiv
    python scripts/main.py --task atel      # 仅运行 ATel
    python scripts/main.py --task arxiv --backfill-start 2026-08-01 --backfill-end 2026-08-10
"""
import os
import json
import time
import datetime
import argparse

from config import ATELS_DIR, POSTS_DIR, STATE_FILE, ARXIV_STATE_FILE
from utils import logger
from arxiv_manager import (
    get_new_arxiv_papers, get_arxiv_papers_for_date, keyword_pre_filter,
    ai_relevance_check, ai_summarize_short,
)
from atel_manager import (
    get_latest_atel_info_from_rss, fetch_atel_detail, ai_summarize_atel,
)
from site_generator import (
    generate_obsidian_note, update_weekly_atel,
    update_source_atel, update_indexes,
)


def run_atel_task():
    """执行 ATel 同步、分析与存储任务。"""
    os.makedirs(ATELS_DIR, exist_ok=True)

    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
    else:
        state = {'last_id': 0, 'pending_ids': []}

    last_id = int(state.get('last_id', 0))
    pending_ids = {
        int(aid) for aid in state.get('pending_ids', [])
        if isinstance(aid, int) or str(aid).isdigit()
    }

    logger.info(
        f"正在同步 ATel (上次记录 ID: {last_id}, "
        f"待重试: {len(pending_ids)})..."
    )
    rss_data = get_latest_atel_info_from_rss()
    max_rss_id = max(rss_data.keys()) if rss_data else last_id
    ids_to_process = sorted(
        pending_ids | set(range(last_id + 1, max_rss_id + 1))
    )

    new_atels = []
    failed_ids = set()

    for aid in ids_to_process:
        detail = None
        for retry in range(2):
            detail = fetch_atel_detail(aid)
            if detail:
                break
            time.sleep(5)

        if not detail:
            logger.warning(f"无法抓取 ATel {aid}，加入待重试队列。")
            failed_ids.add(aid)
            continue

        logger.info(f"  -> 分析 ATel {aid}: {detail['title'][:40]}...")
        ans = ai_summarize_atel(detail)
        if ans:
            new_atels.append({'obj': detail, 'analysis': ans})
        else:
            logger.warning(f"ATel {aid} 分析失败，加入待重试队列。")
            failed_ids.add(aid)

    if new_atels:
        update_weekly_atel(new_atels)
        update_source_atel(new_atels)

    if ids_to_process:
        state['last_id'] = max(last_id, max(ids_to_process))
        state['pending_ids'] = sorted(failed_ids)
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    update_indexes(arxiv_files_updated=False)


def _resolve_arxiv_target_date(papers, requested_date=None):
    """优先使用显式日期，否则采用 Atom feed 的正式公告日期。"""
    if requested_date is not None:
        return requested_date

    announcement_dates = {
        paper.announcement_date
        for paper in papers
        if getattr(paper, 'announcement_date', None) is not None
    }
    if len(announcement_dates) == 1:
        target_date = announcement_dates.pop()
        logger.info(f"使用 arXiv feed 公告日期生成日报: {target_date}")
        return target_date
    if len(announcement_dates) > 1:
        raise ValueError(
            "arXiv feed 同时包含多个公告日期，拒绝写入单个日报: "
            + ", ".join(str(date) for date in sorted(announcement_dates))
        )

    # 搜索 API 回退没有公告日期字段，保留旧行为作为降级路径。
    return datetime.datetime.now(datetime.timezone.utc).date() - datetime.timedelta(days=1)


def run_arxiv_task(target_date=None, backfill_date=None):
    """执行 ArXiv 论文获取、评估与总结任务。"""
    os.makedirs(POSTS_DIR, exist_ok=True)

    if os.path.exists(ARXIV_STATE_FILE):
        with open(ARXIV_STATE_FILE, 'r') as f:
            arxiv_state = json.load(f)
    else:
        arxiv_state = {'processed_ids': []}

    processed_ids = set(arxiv_state.get('processed_ids', []))
    if backfill_date is not None:
        raw_papers = get_arxiv_papers_for_date(
            backfill_date,
            processed_ids,
            max_results=200,
        )
    else:
        raw_papers = get_new_arxiv_papers(processed_ids, max_results=200)
    candidates = keyword_pre_filter(raw_papers)

    if not raw_papers:
        logger.info("没有发现需要分析的新论文。")
        update_indexes(arxiv_files_updated=True)
        return

    target_date = _resolve_arxiv_target_date(raw_papers, target_date)

    # 初始已完成集合：所有未通过关键词初筛的论文
    candidate_entry_ids = {p.entry_id.replace("http://", "https://") for p in candidates}
    finished_ids = {
        p.entry_id.replace("http://", "https://") for p in raw_papers 
        if p.entry_id.replace("http://", "https://") not in candidate_entry_ids
    }

    if candidates:
        logger.info(f"正在使用 Lite 模型为 {len(candidates)} 篇候选论文进行初筛打分...")
        scored_successfully = []
        for p in candidates:
            ans = ai_relevance_check(p)
            p_id = p.entry_id.replace("http://", "https://")
            
            if ans.get('one_sentence_summary') != "解析失败":
                score = ans.get('score', 0)
                scored_successfully.append({'paper': p, 'analysis': ans, 'score': score})
                # 如果分值低，它不需要摘要，直接标记为完成
                if score < 6:
                    finished_ids.add(p_id)
            else:
                logger.warning(f"  [Failed] 论文评分解析失败，稍后重试: {p.title[:30]}...")
            time.sleep(4.0)

        scored_successfully.sort(key=lambda x: x['score'], reverse=True)
        high_score, low_score = [], []

        logger.info("开始生成论文摘要 (高分优先，尝试使用 Flash 模型)...")
        for item in scored_successfully:
            score, p, ans = item['score'], item['paper'], item['analysis']
            p_id = p.entry_id.replace("http://", "https://")

            if score >= 6:
                logger.info(f"  -> [{score}分] {p.title[:30]}...")
                summary = ai_summarize_short(p, ans)
                if not summary.startswith("摘要生成失败"):
                    high_score.append({
                        'paper': p, 'analysis': ans,
                        'summary': summary,
                    })
                    finished_ids.add(p_id)
                else:
                    logger.warning(f"  [Failed] 摘要生成失败，稍后重试: {p.title[:30]}...")
                time.sleep(4.5)
            else:
                # 低分论文已经在上面标记为 finished 了，这里只需加入列表供生成笔记使用
                low_score.append({'paper': p, 'analysis': ans})

        # 仅在有成功解析的论文时才生成笔记
        if high_score or low_score:
            generate_obsidian_note(high_score, low_score, target_date)
        else:
            logger.warning("本次运行未产生任何成功解析的论文。")

    # 更新并持久化状态
    arxiv_state['processed_ids'] = sorted(
        list(processed_ids | finished_ids), reverse=True
    )[:1000]
    with open(ARXIV_STATE_FILE, 'w') as f:
        json.dump(arxiv_state, f, indent=2)

    update_indexes(arxiv_files_updated=True)


def _parse_cli_date(value):
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            f"日期必须为 YYYY-MM-DD: {value}"
        ) from error


def _iter_date_range(start_date, end_date):
    if end_date < start_date:
        raise ValueError("回填结束日期不能早于开始日期")
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += datetime.timedelta(days=1)


def run_arxiv_backfill(start_date, end_date):
    """逐日回填缺失日报，已有文件不覆盖。"""
    for target_date in _iter_date_range(start_date, end_date):
        output_path = os.path.join(
            POSTS_DIR,
            f"Arxiv_Summary_{target_date:%Y-%m-%d}.md",
        )
        if os.path.exists(output_path):
            logger.info(f"日报已存在，跳过回填: {output_path}")
            continue
        run_arxiv_task(target_date=target_date, backfill_date=target_date)
        if target_date < end_date:
            time.sleep(3)


def main():
    parser = argparse.ArgumentParser(description="ArXiv Daily Tracker")
    parser.add_argument(
        '--date',
        type=_parse_cli_date,
        help="仅覆盖正常日更的输出日期 (YYYY-MM-DD)，不用于历史检索",
    )
    parser.add_argument(
        '--backfill-start',
        type=_parse_cli_date,
        help="历史回填开始日期 (YYYY-MM-DD)",
    )
    parser.add_argument(
        '--backfill-end',
        type=_parse_cli_date,
        help="历史回填结束日期 (YYYY-MM-DD，含当日)",
    )
    parser.add_argument('--task', choices=['arxiv', 'atel', 'all'], default='all', help="执行的任务类型")
    args = parser.parse_args()

    backfill_requested = (
        args.backfill_start is not None or args.backfill_end is not None
    )
    if backfill_requested:
        if args.backfill_start is None or args.backfill_end is None:
            parser.error("--backfill-start 和 --backfill-end 必须同时提供")
        if args.task != 'arxiv':
            parser.error("历史回填必须显式指定 --task arxiv")
        if args.date is not None:
            parser.error("历史回填不能与 --date 同时使用")
        try:
            run_arxiv_backfill(args.backfill_start, args.backfill_end)
        except ValueError as error:
            parser.error(str(error))
        return

    if args.task in ['atel', 'all']:
        run_atel_task()

    if args.task in ['arxiv', 'all']:
        run_arxiv_task(args.date)


if __name__ == "__main__":
    main()
