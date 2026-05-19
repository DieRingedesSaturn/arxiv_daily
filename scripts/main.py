"""
ArXiv Daily Tracker - 主入口编排脚本。

用法:
    python scripts/main.py                  # 运行全部任务
    python scripts/main.py --task arxiv     # 仅运行 ArXiv
    python scripts/main.py --task atel      # 仅运行 ATel
    python scripts/main.py --date 2026-04-14  # 指定日期
"""
import os
import json
import time
import datetime
import argparse

from config import ATELS_DIR, POSTS_DIR, STATE_FILE, ARXIV_STATE_FILE
from utils import logger
from arxiv_manager import (
    get_new_arxiv_papers, keyword_pre_filter,
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
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
    else:
        state = {'last_id': 0}

    logger.info(f"正在同步 ATel (上次记录 ID: {state['last_id']})...")
    rss_data = get_latest_atel_info_from_rss()
    max_rss_id = max(rss_data.keys()) if rss_data else state['last_id']

    new_atels = []
    last_success_id = state['last_id']

    for aid in range(state['last_id'] + 1, max_rss_id + 1):
        detail = None
        for retry in range(2):
            detail = fetch_atel_detail(aid)
            if detail:
                break
            time.sleep(5)

        if not detail:
            logger.warning(f"无法抓取 ATel {aid}，跳过此 ID。")
            last_success_id = aid
            continue

        logger.info(f"  -> 分析 ATel {aid}: {detail['title'][:40]}...")
        ans = ai_summarize_atel(detail)
        if ans:
            new_atels.append({'obj': detail, 'analysis': ans})
        last_success_id = aid

    if new_atels:
        update_weekly_atel(new_atels)
        update_source_atel(new_atels)
        state['last_id'] = last_success_id
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)

    update_indexes(arxiv_files_updated=False)


def run_arxiv_task(target_date):
    """执行 ArXiv 论文获取、评估与总结任务。"""
    os.makedirs(POSTS_DIR, exist_ok=True)

    if os.path.exists(ARXIV_STATE_FILE):
        with open(ARXIV_STATE_FILE, 'r') as f:
            arxiv_state = json.load(f)
    else:
        arxiv_state = {'processed_ids': []}

    processed_ids = set(arxiv_state.get('processed_ids', []))
    raw_papers = get_new_arxiv_papers(processed_ids, max_results=200)
    candidates = keyword_pre_filter(raw_papers)

    if not raw_papers:
        logger.info("没有发现需要分析的新论文。")
        update_indexes(arxiv_files_updated=True)
        return

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


def main():
    parser = argparse.ArgumentParser(description="ArXiv Daily Tracker")
    parser.add_argument('--date', type=str, help="目标日期 (YYYY-MM-DD)")
    parser.add_argument('--task', choices=['arxiv', 'atel', 'all'], default='all', help="执行的任务类型")
    args = parser.parse_args()

    if args.task in ['atel', 'all']:
        run_atel_task()

    if args.task in ['arxiv', 'all']:
        target_date = (
            datetime.datetime.strptime(args.date, "%Y-%m-%d").date()
            if args.date
            else datetime.datetime.now(datetime.timezone.utc).date() - datetime.timedelta(days=1)
        )
        run_arxiv_task(target_date)


if __name__ == "__main__":
    main()