"""
站点生成模块：Markdown 笔记、周报、索引页面的生成与更新。

输出格式与已有 docs/ 目录下的 Markdown 文件完全兼容。
"""
import os
import re
import json
import datetime

from config import (
    POSTS_DIR, ATELS_DIR, SOURCE_MAP_FILE,
    ARXIV_CATEGORIES, SOURCE_CATEGORIES,
)
from utils import (
    logger, get_iso_week, get_canonical_name, init_source_map_from_files,
)


# ================= ArXiv 笔记 =================
def generate_obsidian_note(high_score_papers: list, low_score_papers: list, target_date) -> str | None:
    """生成 ArXiv 每日笔记 Markdown 文件。返回生成的文件路径。"""
    if not high_score_papers and not low_score_papers:
        return None

    high_score_papers.sort(key=lambda x: x['analysis']['score'], reverse=True)
    low_score_papers.sort(key=lambda x: x['analysis']['score'], reverse=True)
    date_str = target_date.strftime("%Y-%m-%d")
    file_path = os.path.join(POSTS_DIR, f"Arxiv_Summary_{date_str}.md")
    os.makedirs(POSTS_DIR, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(
            f"# arXiv Daily: {date_str}\n\n"
            f"*Tags: #arXiv #Astrophysics*\n\n"
            f"## 重点关注 ({len(high_score_papers)}篇)\n\n"
        )
        if not high_score_papers:
            f.write("今日无重点推荐。\n\n")

        for item in high_score_papers:
            p, ans, summ = item['paper'], item['analysis'], item['summary']
            targets = ", ".join(ans.get('target_objects', []))
            td = f" | **Targets**: {targets}" if targets else ""
            f.write(
                f"### [{ans['score']}] | [{p.title}]({p.entry_id})\n"
                f"**Authors**: {', '.join([a.name for a in p.authors[:3]])} et al.{td}\n\n"
                f"> *{ans['one_sentence_summary']}*\n\n"
                f"{summ}\n\n---\n\n"
            )

        f.write(f"## 其他相关 ({len(low_score_papers)}篇)\n\n")
        for item in low_score_papers:
            f.write(
                f"- **[{item['analysis']['score']}]** [{item['paper'].title}]({item['paper'].entry_id})\n"
                f"  - *{item['analysis']['one_sentence_summary']}*\n"
            )

    return file_path


# ================= ATel 周报 =================
def update_weekly_atel(new_items: list):
    """按 ISO 周将新 ATel 条目追加到对应的周报文件。"""
    os.makedirs(ATELS_DIR, exist_ok=True)
    weeks = {}
    for item in new_items:
        weeks.setdefault(get_iso_week(item['obj']['date']), []).append(item)

    for week, items in weeks.items():
        file_path = os.path.join(ATELS_DIR, f"{week}.md")
        items.sort(key=lambda x: x['obj']['id'], reverse=True)

        new_block = ""
        for i in items:
            new_block += (
                f"### [{i['analysis']['score']}] | ATel {i['obj']['id']}: "
                f"[{i['obj']['title']}]({i['obj']['link']})\n"
                f"- **日期**: {i['obj']['date']} | **源**: `{i['analysis'].get('object_name', 'Unknown')}`\n\n"
                f"{i['analysis']['summary_md']}\n\n---\n\n"
            )

        old_content = ""
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'### ', content)
                if match:
                    old_content = content[match.start():]

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# ATel Weekly: {week}\n\n*Tags: #ATel*\n\n---\n\n" + new_block + old_content)


# ================= ATel 源追踪 =================
def update_source_atel(new_items: list):
    """按天体源更新/创建每个源的追踪文件。"""
    sources_dir = os.path.join(ATELS_DIR, "sources")
    os.makedirs(sources_dir, exist_ok=True)

    if os.path.exists(SOURCE_MAP_FILE):
        with open(SOURCE_MAP_FILE, 'r', encoding='utf-8') as f:
            source_map = json.load(f)
    else:
        source_map = init_source_map_from_files(sources_dir)

    for item in new_items:
        obj, ans = item['obj'], item['analysis']
        raw_name = ans.get('object_name', 'Unknown').strip()
        if not raw_name or raw_name.lower() == 'unknown':
            continue

        s_name = get_canonical_name(raw_name, ans.get('aliases', []), source_map)
        file_path = os.path.join(sources_dir, f"{s_name}.md")
        cls = ans.get('classification', 'Other')
        entry = (
            f"### ATel {obj['id']}: [{obj['title']}]({obj['link']})\n"
            f"- **日期**: {obj['date']}\n\n"
            f"{ans['summary_md']}\n\n---\n\n"
        )

        old_content = ""
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'### ', content)
                if match:
                    old_content = content[match.start():]

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(
                f"# Source: {s_name.replace('___', ' / ').replace('_', ' ')}\n\n"
                f"*Tags: #ATel #{cls}*\n\n"
                f"- **类别**: {cls}\n\n---\n\n"
                + entry + old_content
            )

    with open(SOURCE_MAP_FILE, 'w', encoding='utf-8') as f:
        json.dump(source_map, f, ensure_ascii=False, indent=2)


# ================= 索引生成 =================
def update_indexes(arxiv_files_updated: bool = True):
    """重新生成 ArXiv 目录、ATel 索引和首页。"""

    # --- ArXiv 索引 ---
    if arxiv_files_updated:
        files = sorted(
            [f for f in os.listdir(POSTS_DIR) if f.startswith("Arxiv_Summary_") and f.endswith(".md")],
            reverse=True,
        )
        with open(os.path.join(POSTS_DIR, "index.md"), 'w', encoding='utf-8') as f:
            f.write(
                "# ArXiv 目录\n\n"
                + "\n".join([f"- [{fn.replace('Arxiv_Summary_', '').replace('.md', '')}]({fn})" for fn in files])
            )

    # --- ATel 索引 ---
    w_files = sorted(
        [f for f in os.listdir(ATELS_DIR) if f.endswith(".md") and "-W" in f],
        reverse=True,
    )
    s_dir = os.path.join(ATELS_DIR, "sources")
    s_list = []
    if os.path.exists(s_dir):
        for sf in os.listdir(s_dir):
            if not sf.endswith(".md"):
                continue
            # 性能优化：仅读取文件头部 1KB 即可获取元数据
            with open(os.path.join(s_dir, sf), 'r', encoding='utf-8') as f:
                c = f.read(1024)
            # 兼容性正则：支持不同语言和格式
            m_cat = re.search(r'-\s*\*\*[^:*]+\*\*[:\s]+(.*)', c)
            m_id = re.search(r'### ATel (\d+):', c)
            m_dt = re.search(r'-\s*\*\*[^:*]+\*\*[:\s]+(\d{1,2}\s+[A-Za-z]+\s+\d{4})', c)
            dt_str = m_dt.group(1).strip() if m_dt else "01 Jan 1970"
            try:
                parsed_dt = datetime.datetime.strptime(dt_str, "%d %b %Y")
            except ValueError:
                parsed_dt = datetime.datetime(1970, 1, 1)
            s_list.append({
                'name': sf.replace(".md", ""),
                'file': sf,
                'cat': m_cat.group(1).strip() if m_cat else "Other",
                'date': parsed_dt,
                'date_str': dt_str,
                'atel_id': m_id.group(1).strip() if m_id else "未知",
            })

    s_list.sort(key=lambda x: x['date'], reverse=True)

    with open(os.path.join(ATELS_DIR, "index.md"), 'w', encoding='utf-8') as f:
        f.write(
            "# ATel 索引\n\n## 按周汇总\n"
            + "\n".join([f"- [{wf.replace('.md', '')}]({wf})" for wf in w_files])
            + "\n\n## 爆发源追踪 (按更新日期排列)\n"
        )
        for cat in SOURCE_CATEGORIES:
            cat_items = [s for s in s_list if s['cat'] == cat]
            if cat_items:
                f.write(
                    f"\n### {cat}\n"
                    + "\n".join([
                        f"- [{i['name']}](./sources/{i['file']}) | *最新动态: ATel {i['atel_id']} ({i['date_str']})*"
                        for i in cat_items
                    ])
                    + "\n"
                )

    # --- 首页 ---
    snippet = "暂无记录"
    if w_files:
        with open(os.path.join(ATELS_DIR, w_files[0]), 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'### ', content)
        if match:
            snippet_raw = content[match.start():]
            snippet = "\n".join(snippet_raw.splitlines()[:15])
        else:
            snippet = "暂无记录"
        snippet += f"\n\n[查看本周完整 ATel](./atels/{w_files[0]})"

    with open("./docs/index.md", 'w', encoding='utf-8') as f:
        f.write(
            f"# ArXiv Daily Tracker\n\n"
            f"> 专注于高能天体物理与暂现源追踪，涵盖吸积物理、双星演化等。\n\n"
            f"## 监控配置\n"
            f"- **arXiv 分类**: `{', '.join(ARXIV_CATEGORIES)}`\n"
            f"- **ATel 范围**: 17680 之后\n"
            f"## 最新天文简报 (ATel)\n\n{snippet}\n\n"
            f"[查看所有 ATel 索引](./atels/index.md)\n\n---\n\n"
            f"## 最新论文 (arXiv)\n"
        )
        arx_files = sorted(
            [fn for fn in os.listdir(POSTS_DIR) if fn.startswith("Arxiv_Summary_") and fn.endswith(".md")],
            reverse=True,
        )
        if arx_files:
            with open(os.path.join(POSTS_DIR, arx_files[0]), 'r', encoding='utf-8') as arx_f:
                f.write("".join(arx_f.readlines()[1:]) + "\n[查看历史目录](./posts/index.md)\n")
        else:
            f.write("今日无更新\n")
