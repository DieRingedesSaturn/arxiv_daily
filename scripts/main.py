import os
import datetime
import time
import arxiv
import argparse
import requests
import random
import re
import json
from bs4 import BeautifulSoup

# 导入拆分出去的模块
from config import *
from schemas import SourceAliases, PaperEvaluation, ATelAnalysis
from llm_api import generate_content_with_retry

try:
    from astroquery.simbad import Simbad
except ImportError:
    print("[Error] 缺少 astroquery 库。请运行: pip install astroquery")
    Simbad = None

# ================= 名称解析逻辑 =================
def normalize_source_name(name: str) -> str:
    if not name: return ""
    name = re.sub(r'\(.*?\)', '', name)
    name = re.sub(r'^(SOURCE|OBJECT)[:\s]+', '', name, flags=re.IGNORECASE)
    return re.sub(r'[^A-Z0-9\+\-\._]', '', name.upper())

def get_aliases_from_simbad(primary_name: str) -> list[str]:
    if not Simbad: return []
    try:
        result_table = Simbad.query_objectids(primary_name)
        if result_table is not None:
            aliases = []
            for row in result_table:
                val = row[0].decode('utf-8') if isinstance(row[0], bytes) else str(row[0])
                aliases.append(val.strip())
            return aliases
        return []
    except Exception as e:
        print(f"  [SIMBAD] 未找到 '{primary_name}' 的官方别名: {e}")
        return []

def get_canonical_name(name: str, aliases: list[str], source_map: dict) -> str:
    all_names = [name] + (aliases if aliases else [])
    
    def find_in_map(names):
        for n in names:
            norm = normalize_source_name(n)
            if norm and norm in source_map: return source_map[norm]
        return None

    result = find_in_map(all_names)
    if result: return result
    
    print(f"  [SIMBAD] 正在为新源 '{name}' 拉取天文台标准别名以防重叠...")
    simbad_aliases = get_aliases_from_simbad(name)
    result = find_in_map(simbad_aliases)
    if result:
        norm = normalize_source_name(name)
        if norm: source_map[norm] = result
        return result
            
    new_canonical = name.strip().replace("/", "_").replace(" ", "_")
    for n in all_names + simbad_aliases:
        norm = normalize_source_name(n)
        if norm: source_map[norm] = new_canonical
    return new_canonical

def init_source_map_from_files(sources_dir: str) -> dict:
    source_map = {}
    if not os.path.exists(sources_dir): return source_map
    for f in os.listdir(sources_dir):
        if not f.endswith(".md"): continue
        canonical = f.replace(".md", "")
        for n in canonical.split("___"):
            norm = normalize_source_name(n)
            if norm: source_map[norm] = canonical
    return source_map

# ================= arXiv 逻辑 =================
def get_new_arxiv_papers(processed_ids: set[str], max_results: int = 200) -> list[arxiv.Result]:
    print(f"[System] 正在检索最新的 {max_results} 篇 arXiv 论文...")
    query = ' OR '.join([f'cat:{c}' for c in ARXIV_CATEGORIES])
    search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.SubmittedDate)
    client_arxiv = arxiv.Client(page_size=100, delay_seconds=3, num_retries=3)
    
    new_papers = [res for res in client_arxiv.results(search) if res.entry_id.replace("http://", "https://") not in processed_ids]
    print(f"[System] 过滤后发现 {len(new_papers)} 篇未处理的新论文。")
    return new_papers

def keyword_pre_filter(papers: list[arxiv.Result]) -> list[arxiv.Result]:
    candidates = [p for p in papers if any(k.lower() in (p.title + " " + p.summary).lower() for k in KEYWORDS_BROAD)]
    print(f"[Filter] 关键词初筛后剩余: {len(candidates)} 篇")
    return candidates

def ai_relevance_check(paper):
    prompt = f"""
    任务：作为天体物理教授，评估以下论文与课题组研究兴趣的相关性。

    【研究兴趣】
    {RESEARCH_INTEREST}

    【论文信息】
    Title: {paper.title}
    Abstract: {paper.summary}
    """
    # 打分阶段：优先免费 Lite -> 兜底付费 Lite
    try:
        return generate_content_with_retry(model=GEMINI_MODEL_LITE, contents=prompt, schema=PaperEvaluation, provider="google", max_retries=3)
    except Exception as e:
        print(f"  [Fallback] 免费 Lite 打分拥堵，切换付费 Lite...")
        try:
            return generate_content_with_retry(model=GEMINI_MODEL_LITE, contents=prompt, schema=PaperEvaluation, provider="openai", max_retries=2)
        except Exception:
            return {"score": 0, "one_sentence_summary": "解析失败", "target_objects": []}

def ai_summarize_short(paper, analysis_info):
    prompt = f"""
    任务：为天体物理学者提供该论文的前沿速览，辅助高效筛选和深度阅读每日 arXiv。

    Title: {paper.title}
    Abstract: {paper.summary}
    AI识别天体: {analysis_info.get('target_objects', [])}

    请用中文输出，总字数控制在 250 字左右。
    严格禁止使用任何 Markdown 标题语法（如 `#`、`##` 等）。
    请直接使用加粗文本作为段落引导，采用以下三段式结构详细概括原摘要：
    
    **研究背景**: (简述该研究针对的物理问题、长期争议或此次观测的动机)
    **数据方法**: (说明使用了哪些具体望远镜的数据，或是采用了什么理论推导/数据拟合模型)
    **核心结论**: (阐述研究得到的核心结果，以及这对现有物理图像的推进。)

    请用中文输出，总字数控制在 250 字左右。
    """
    # 摘要阶段：免费 Flash -> 免费 Lite -> 付费 Lite (严格控制成本)
    try:
        return generate_content_with_retry(model=GEMINI_MODEL_FLASH, contents=prompt, max_retries=2, base_delay=2, provider="google")
    except Exception as e1:
        print(f"  [Fallback 1] 免费 Flash 失败，降级免费 Lite...")
        try:
            return generate_content_with_retry(model=GEMINI_MODEL_LITE, contents=prompt, max_retries=2, base_delay=2, provider="google")
        except Exception as e2:
            print(f"  [Fallback 2] 免费路线全挂，启用第三方付费 lite 兜底...")
            try:
                return generate_content_with_retry(model=GEMINI_MODEL_LITE, contents=prompt, max_retries=2, provider="openai")
            except Exception as e3:
                return f"摘要生成失败: {e3}"


def generate_obsidian_note(high_score_papers, low_score_papers, target_date):
    if not high_score_papers and not low_score_papers: return None
    high_score_papers.sort(key=lambda x: x['analysis']['score'], reverse=True)
    low_score_papers.sort(key=lambda x: x['analysis']['score'], reverse=True)
    date_str = target_date.strftime("%Y-%m-%d")
    file_path = os.path.join(POSTS_DIR, f"Arxiv_Summary_{date_str}.md")
    os.makedirs(POSTS_DIR, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"# arXiv Daily: {date_str}\n\n*Tags: #arXiv #Astrophysics*\n\n## 重点关注 ({len(high_score_papers)}篇)\n\n")
        if not high_score_papers: f.write("今日无重点推荐。\n\n")
        for item in high_score_papers:
            p, ans, summ = item['paper'], item['analysis'], item['summary']
            targets = ", ".join(ans.get('target_objects', []))
            td = f" | **Targets**: {targets}" if targets else ""
            f.write(f"### [{ans['score']}] | [{p.title}]({p.entry_id})\n**Authors**: {', '.join([a.name for a in p.authors[:3]])} et al.{td}\n\n> *{ans['one_sentence_summary']}*\n\n{summ}\n\n---\n\n")
            
        f.write(f"## 其他相关 ({len(low_score_papers)}篇)\n\n")
        for item in low_score_papers:
            f.write(f"- **[{item['analysis']['score']}]** [{item['paper'].title}]({item['paper'].entry_id})\n  - *{item['analysis']['one_sentence_summary']}*\n")
    return file_path

# ================= ATel 逻辑 =================
def get_latest_atel_info_from_rss():
    import feedparser
    try:
        feed = feedparser.parse(requests.get(ATEL_RSS_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30).text)
        return {int(e.link.split('=')[-1]): e for e in feed.entries}
    except: return {}

def fetch_atel_detail(atel_id):
    url = f"{ATEL_BASE_URL}/?read={atel_id}"
    try:
        wait_time = random.uniform(8, 15)
        print(f"  [Scraper] 正在抓取 ATel {atel_id} (等待 {wait_time:.1f}s)...")
        time.sleep(wait_time)
        soup = BeautifulSoup(requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30).text, 'html.parser')
        if soup.find(id='time'): soup.find(id='time').decompose()
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else f"ATel {atel_id}"
        title = title.replace(f"ATel {atel_id}: ", "")
        
        full_text = soup.get_text(separator=' ')
        date_str = "Unknown Date"
        if m := re.search(r'on\s+(\d{1,2}\s+[A-Za-z]{3,}\s+\d{4});\s+\d{2}:\d{2}\s+UT', full_text) or re.search(r'(\d{1,2}\s+[A-Za-z]{3,}\s+\d{4}).*?UT', full_text):
            date_str = m.group(1).strip() + " UT"
            
        # --- 优化后的正文提取逻辑 ---
        content = ""
        # 1. 优先尝试标准的 teltext 容器
        content_div = soup.find('div', id='teltext')
        if content_div:
            content = content_div.get_text(separator='\n', strip=True)
        
        # 2. 如果没有 teltext，则寻找 subjects 之后的所有段落
        if not content:
            subjects_div = soup.find('div', id='subjects')
            if subjects_div:
                paragraphs = []
                # 查找 subjects 之后的所有兄弟节点中的段落 (支持大小写 P)
                for sibling in subjects_div.find_next_siblings(['p', 'P']):
                    txt = sibling.get_text(strip=True)
                    # 排除掉社交媒体按钮等干扰项
                    if txt and "Tweet" not in txt and len(txt) > 5:
                        paragraphs.append(txt)
                content = "\n\n".join(paragraphs)
        
        # 3. 最后的保底方案：抓取所有较长的段落
        if not content:
            all_p = soup.find_all(['p', 'P'])
            content = "\n\n".join([p.get_text(strip=True) for p in all_p if len(p.get_text()) > 50 and "Tweet" not in p.get_text()])

        return {'id': atel_id, 'title': title, 'date': date_str, 'content': content, 'link': url}
    except Exception as e:
        print(f"[Error] 抓取 ATel {atel_id} 失败: {e}")
        return None

def ai_summarize_atel(atel):
    prompt = f"""
    任务：分析 ATel 简报，提取核心信息并做极简总结。

    【研究兴趣与设备能力】
    {RESEARCH_INTEREST}

    【ATel 信息】
    Title: {atel['title']}
    Content: {atel['content']}
    """
    # ATel阶段：直接使用 Lite 模型 (免费额度大且效果稳定)
    try:
        return generate_content_with_retry(model=GEMINI_MODEL_LITE, contents=prompt, schema=ATelAnalysis, max_retries=3, base_delay=5, provider="google")
    except Exception as e:
        print(f"  [Fallback] ATel 免费 Lite 线路受限，尝试第三方付费 Lite 兜底...")
        try:
            return generate_content_with_retry(model=GEMINI_MODEL_LITE, contents=prompt, schema=ATelAnalysis, max_retries=2, provider="openai")
        except Exception:
            return None

# ================= 存储与索引 =================
def get_iso_week(date_str: str):
    try:
        # 预处理日期字符串，提取 日、月、年
        # 示例: "12 Mar 2026 UT" 或 "12 March 2026"
        m = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', date_str)
        if not m: return f"{datetime.datetime.now().isocalendar()[0]}-W{datetime.datetime.now().isocalendar()[1]:02d}"
        
        day, mon, year = m.group(1), m.group(2)[:3].capitalize(), m.group(3)
        clean_date = f"{day} {mon} {year}"
        dt = datetime.datetime.strptime(clean_date, '%d %b %Y')
        return f"{dt.isocalendar()[0]}-W{dt.isocalendar()[1]:02d}"
    except Exception as e:
        print(f"  [Warning] 日期解析失败 '{date_str}': {e}")
        return f"{datetime.datetime.now().isocalendar()[0]}-W{datetime.datetime.now().isocalendar()[1]:02d}"

def update_weekly_atel(new_items):
    os.makedirs(ATELS_DIR, exist_ok=True)
    weeks = {}
    for item in new_items:
        weeks.setdefault(get_iso_week(item['obj']['date']), []).append(item)
        
    for week, items in weeks.items():
        file_path = os.path.join(ATELS_DIR, f"{week}.md")
        items.sort(key=lambda x: x['obj']['id'], reverse=True)
        new_block = ""
        for i in items:
            new_block += f"### [{i['analysis']['score']}] | ATel {i['obj']['id']}: [{i['obj']['title']}]({i['obj']['link']})\n- **日期**: {i['obj']['date']} | **源**: `{i['analysis'].get('object_name', 'Unknown')}`\n\n{i['analysis']['summary_md']}\n\n---\n\n"
            
        old_content = ""
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 查找第一个条目标题的位置，从而跳过旧的头部
                match = re.search(r'### ', content)
                if match:
                    old_content = content[match.start():]
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# ATel Weekly: {week}\n\n*Tags: #ATel*\n\n---\n\n" + new_block + old_content)

def update_source_atel(new_items):
    sources_dir = os.path.join(ATELS_DIR, "sources")
    os.makedirs(sources_dir, exist_ok=True)
    source_map = json.load(open(SOURCE_MAP_FILE, 'r', encoding='utf-8')) if os.path.exists(SOURCE_MAP_FILE) else init_source_map_from_files(sources_dir)

    for item in new_items:
        obj, ans = item['obj'], item['analysis']
        raw_name = ans.get('object_name', 'Unknown').strip()
        if not raw_name or raw_name.lower() == 'unknown': continue
        
        s_name = get_canonical_name(raw_name, ans.get('aliases', []), source_map)
        file_path = os.path.join(sources_dir, f"{s_name}.md")
        cls = ans.get('classification', 'Other')
        entry = f"### ATel {obj['id']}: [{obj['title']}]({obj['link']})\n- **日期**: {obj['date']}\n\n{ans['summary_md']}\n\n---\n\n"
        
        old_content = ""
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'### ', content)
                if match:
                    old_content = content[match.start():]
                
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# Source: {s_name.replace('___', ' / ').replace('_', ' ')}\n\n*Tags: #ATel #{cls}*\n\n- **类别**: {cls}\n\n---\n\n" + entry + old_content)
            
    with open(SOURCE_MAP_FILE, 'w', encoding='utf-8') as f: json.dump(source_map, f, ensure_ascii=False, indent=2)

def update_indexes(arxiv_files_updated=True):
    # ArXiv Index
    if arxiv_files_updated:
        files = sorted([f for f in os.listdir(POSTS_DIR) if f.startswith("Arxiv_Summary_") and f.endswith(".md")], reverse=True)
        with open(os.path.join(POSTS_DIR, "index.md"), 'w', encoding='utf-8') as f:
            f.write("# ArXiv 目录\n\n" + "\n".join([f"- [{fn.replace('Arxiv_Summary_', '').replace('.md', '')}]({fn})" for fn in files]))
            
    # ATel Index
    w_files = sorted([f for f in os.listdir(ATELS_DIR) if f.endswith(".md") and "-W" in f], reverse=True)
    s_dir, s_list = os.path.join(ATELS_DIR, "sources"), []
    if os.path.exists(s_dir):
        for sf in os.listdir(s_dir):
            if not sf.endswith(".md"): continue
            # 性能优化：仅读取文件头部 1KB 即可获取元数据
            with open(os.path.join(s_dir, sf), 'r', encoding='utf-8') as f:
                c = f.read(1024)
            # 兼容性正则：支持不同语言和格式
            m_cat = re.search(r'-\s*\*\*[^:*]+\*\*[:\s]+(.*)', c) 
            m_id = re.search(r'### ATel (\d+):', c)
            m_dt = re.search(r'-\s*\*\*[^:*]+\*\*[:\s]+(\d{1,2}\s+[A-Za-z]+\s+\d{4})', c)
            dt_str = m_dt.group(1).strip() if m_dt else "01 Jan 1970"
            try: parsed_dt = datetime.datetime.strptime(dt_str, "%d %b %Y")
            except: parsed_dt = datetime.datetime(1970, 1, 1)
            s_list.append({'name': sf.replace(".md", ""), 'file': sf, 'cat': m_cat.group(1).strip() if m_cat else "Other", 'date': parsed_dt, 'date_str': dt_str, 'atel_id': m_id.group(1).strip() if m_id else "未知"})
            
    s_list.sort(key=lambda x: x['date'], reverse=True)
    with open(os.path.join(ATELS_DIR, "index.md"), 'w', encoding='utf-8') as f:
        f.write("# ATel 索引\n\n## 按周汇总\n" + "\n".join([f"- [{wf.replace('.md', '')}]({wf})" for wf in w_files]) + "\n\n## 爆发源追踪 (按更新日期排列)\n")
        for cat in SOURCE_CATEGORIES:
            cat_items = [s for s in s_list if s['cat'] == cat]
            if cat_items:
                f.write(f"\n### {cat}\n" + "\n".join([f"- [{i['name']}](./sources/{i['file']}) | *最新动态: ATel {i['atel_id']} ({i['date_str']})*" for i in cat_items]) + "\n")

    # Home Page
    snippet = "暂无记录"
    if w_files:
        content = open(os.path.join(ATELS_DIR, w_files[0]), 'r', encoding='utf-8').read()
        match = re.search(r'### ', content)
        if match:
            # 获取第一个条目开始后的前 15 行作为摘要
            snippet_raw = content[match.start():]
            snippet = "\n".join(snippet_raw.splitlines()[:15])
        else:
            snippet = "暂无记录"
        snippet += f"\n\n[查看本周完整 ATel](./atels/{w_files[0]})"
    
    with open("./docs/index.md", 'w', encoding='utf-8') as f:
        f.write(f"# ArXiv Daily Tracker\n\n> 专注于高能天体物理与暂现源追踪，涵盖吸积物理、双星演化等。\n\n## 监控配置\n- **arXiv 分类**: `{', '.join(ARXIV_CATEGORIES)}`\n- **ATel 范围**: 17680 之后\n## 最新天文简报 (ATel)\n\n{snippet}\n\n[查看所有 ATel 索引](./atels/index.md)\n\n---\n\n## 最新论文 (arXiv)\n")
        arx_files = sorted([f for f in os.listdir(POSTS_DIR) if f.startswith("Arxiv_Summary_") and f.endswith(".md")], reverse=True)
        if arx_files:
            f.write("".join(open(os.path.join(POSTS_DIR, arx_files[0]), 'r', encoding='utf-8').readlines()[1:]) + "\n[查看历史目录](./posts/index.md)\n")
        else: f.write("今日无更新\n")

# ================= 主函数 =================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', type=str)
    parser.add_argument('--task', choices=['arxiv', 'atel', 'all'], default='all')
    args = parser.parse_args()

    if args.task in ['atel', 'all']:
        os.makedirs(ATELS_DIR, exist_ok=True)
        state = json.load(open(STATE_FILE, 'r')) if os.path.exists(STATE_FILE) else {'last_id': 0}
        print(f"[System] 正在同步 ATel (上次记录 ID: {state['last_id']})...")
        rss_data = get_latest_atel_info_from_rss()
        max_rss_id = max(rss_data.keys()) if rss_data else state['last_id']
        new_atels = []
        last_success_id = state['last_id']
        for aid in range(state['last_id'] + 1, max_rss_id + 1):
            detail = None
            for retry in range(2): # 允许重试一次
                detail = fetch_atel_detail(aid)
                if detail: break
                time.sleep(5)
            
            if not detail: 
                print(f"[Warning] 无法抓取 ATel {aid}，跳过此 ID。")
                last_success_id = aid # 跳过并标记为已处理
                continue

            print(f"  -> 分析 ATel {aid}: {detail['title'][:40]}...")
            ans = ai_summarize_atel(detail)
            if ans: 
                new_atels.append({'obj': detail, 'analysis': ans})
                last_success_id = aid
            else:
                # 如果 AI 解析失败但抓取成功，也视为处理过（可能是内容不符合 Schema）
                last_success_id = aid
            
        if new_atels:
            update_weekly_atel(new_atels)
            update_source_atel(new_atels)
            state['last_id'] = last_success_id
            with open(STATE_FILE, 'w') as f: json.dump(state, f)
        update_indexes(arxiv_files_updated=False)

    if args.task in ['arxiv', 'all']:
        os.makedirs(POSTS_DIR, exist_ok=True)
        arxiv_state = json.load(open(ARXIV_STATE_FILE, 'r')) if os.path.exists(ARXIV_STATE_FILE) else {'processed_ids': []}
        processed_ids = set(arxiv_state.get('processed_ids', []))
        
        target_date = datetime.datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else datetime.datetime.now(datetime.timezone.utc).date() - datetime.timedelta(days=1)
            
        raw_papers = get_new_arxiv_papers(processed_ids, max_results=200)
        candidates = keyword_pre_filter(raw_papers)
        
        if candidates:
            print(f"[System] 正在使用 Lite 模型为 {len(candidates)} 篇候选论文进行初筛打分...")
            scored = []
            for p in candidates:
                ans = ai_relevance_check(p)
                scored.append({'paper': p, 'analysis': ans, 'score': ans.get('score', 0)})
                time.sleep(4.0)
            
            scored.sort(key=lambda x: x['score'], reverse=True)
            high_score, low_score = [], []
            
            print(f"[System] 开始生成论文摘要 (高分优先，尝试使用 Flash 模型)...")
            for item in scored:
                score, p, ans = item['score'], item['paper'], item['analysis']
                print(f"  -> [{score}分] {p.title[:30]}...")
                if score >= 6:
                    high_score.append({'paper': p, 'analysis': ans, 'summary': ai_summarize_short(p, ans)})
                    time.sleep(4.5)
                else:
                    low_score.append({'paper': p, 'analysis': ans})
                    
            generate_obsidian_note(high_score, low_score, target_date)
            new_ids = [p.entry_id.replace("http://", "https://") for p in raw_papers]
            arxiv_state['processed_ids'] = sorted(list(processed_ids | set(new_ids)), reverse=True)[:1000]
            with open(ARXIV_STATE_FILE, 'w') as f: json.dump(arxiv_state, f, indent=2)
        else:
            print("[System] 没有发现需要分析的新论文。")
            
        update_indexes(arxiv_files_updated=True)

if __name__ == "__main__":
    main()