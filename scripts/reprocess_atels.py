"""
批量重处理历史 ATel 数据的工具脚本。
从已有的周总结文件中提取 ATel ID，重新抓取并用 AI 分析归类。
"""
import os
import re
import time
import argparse

from config import ATELS_DIR
from utils import logger
from atel_manager import fetch_atel_detail, ai_summarize_atel
from site_generator import update_source_atel, update_indexes


def extract_atel_ids_from_summaries() -> list[int]:
    """从 docs/atels/ 目录下的周总结 MD 文件中提取所有 ATel ID"""
    atel_ids = set()
    if not os.path.exists(ATELS_DIR):
        return []

    pattern = re.compile(r'astronomerstelegram\.org/\?read=(\d+)')

    for filename in os.listdir(ATELS_DIR):
        if filename.endswith(".md") and "-W" in filename:
            file_path = os.path.join(ATELS_DIR, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = pattern.findall(content)
                for m in matches:
                    atel_ids.add(int(m))

    sorted_ids = sorted(list(atel_ids))
    logger.info(f"从历史周总结中提取到 {len(sorted_ids)} 个唯一的 ATel ID。")
    return sorted_ids


def reprocess_all():
    """
    重新处理所有 ATel：重新抓取、AI 分析、更新源文件。
    """
    ids = extract_atel_ids_from_summaries()

    if not ids:
        logger.error("未找到任何可处理的 ATel ID。")
        return

    new_items_for_sources = []

    for aid in ids:
        detail = fetch_atel_detail(aid)
        if not detail:
            continue

        logger.info(f"  -> 正在重新分析 ATel {aid}: {detail['title'][:50]}...")
        ans = ai_summarize_atel(detail)
        if ans:
            new_items_for_sources.append({'obj': detail, 'analysis': ans})
            time.sleep(2)

            # 每 5 条更新一次，防止崩溃丢失进度
            if len(new_items_for_sources) >= 5:
                update_source_atel(new_items_for_sources)
                new_items_for_sources = []

    # 处理最后一批
    if new_items_for_sources:
        update_source_atel(new_items_for_sources)

    # 重新生成总索引
    logger.info("正在重新生成 ATel 索引...")
    update_indexes(arxiv_files_updated=False)
    logger.info("全量重处理完成。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="重新处理历史 ATel 数据并分类")
    parser.add_argument('--full', action='store_true', help='执行全量重处理')
    args = parser.parse_args()

    logger.warning("注意：此操作将调用 Gemini API 重新分析历史数据，可能产生较多 Token 消耗。")
    reprocess_all()
