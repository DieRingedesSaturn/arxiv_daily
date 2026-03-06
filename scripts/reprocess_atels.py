import os
import re
import json
import time
import argparse
from main import (
    get_gemini_client, fetch_atel_detail, ai_summarize_atel, 
    update_source_atel, update_atels_index, ATELS_DIR, SOURCE_MAP_FILE
)

def extract_atel_ids_from_summaries():
    """从 docs/atels/ 目录下的周总结 MD 文件中提取所有 ATel ID"""
    atel_ids = set()
    if not os.path.exists(ATELS_DIR):
        return []
    
    # 匹配模式：[Title](https://www.astronomerstelegram.org/?read=ID)
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
    print(f"[System] 从历史周总结中提取到 {len(sorted_ids)} 个唯一的 ATel ID。")
    return sorted_ids

def reprocess_all(force_ai=False):
    """
    重新处理所有 ATel。
    force_ai: 是否强制重新运行 AI 分析（即使源已经存在）。
    """
    client = get_gemini_client()
    ids = extract_atel_ids_from_summaries()
    
    if not ids:
        print("[Error] 未找到任何可处理的 ATel ID。")
        return

    # 如果需要彻底重新分类，可以考虑清空 source_map 但保留文件
    # 这里我们选择保留映射，利用 get_canonical_name 的别名扩展能力进行合并
    
    new_items_for_sources = []
    
    for aid in ids:
        # 抓取详细内容
        detail = fetch_atel_detail(aid)
        if not detail:
            continue
        
        print(f"  -> 正在重新分析 ATel {aid}: {detail['title'][:50]}...")
        
        # 让 AI 重新总结并识别源/别名
        ans = ai_summarize_atel(client, detail)
        if ans:
            new_items_for_sources.append({'obj': detail, 'analysis': ans})
            
            # 为了防止批量请求被封或超过 Flash 频率限制，稍微等待
            time.sleep(2)
            
            # 每一批次更新一次，防止程序崩溃丢失进度
            if len(new_items_for_sources) >= 5:
                update_source_atel(new_items_for_sources, client=client)
                new_items_for_sources = []

    # 处理最后一批
    if new_items_for_sources:
        update_source_atel(new_items_for_sources, client=client)

    # 重新生成总索引
    print("[System] 正在重新生成 ATel 索引...")
    update_atels_index()
    print("[Success] 全量重处理完成。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="重新处理历史 ATel 数据并分类")
    parser.add_argument('--full', action='store_true', help='执行全量重处理')
    args = parser.parse_args()
    
    print("注意：此操作将调用 Gemini API 重新分析历史数据，可能产生较多 Token 消耗。")
    reprocess_all()
