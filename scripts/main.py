import os
import datetime
import json
import time
import pytz
import arxiv
import argparse
import requests
import random
import re
from bs4 import BeautifulSoup
from google import genai
from google.genai import types

# ================= 配置区域 =================

# Google Gemini API Key
API_KEY = os.environ.get("GOOGLE_API_KEY", "xxx")

# arXiv 搜索配置
ARXIV_CATEGORIES = ["astro-ph.HE", "astro-ph.SR"]

# ATel 配置
ATEL_BASE_URL = "https://www.astronomerstelegram.org"
ATEL_RSS_URL = f"{ATEL_BASE_URL}/?rss"

# 爆发源分类词库
SOURCE_CATEGORIES = ["BHXRB", "NSXRB", "CV", "AGN", "TDE", "GRB", "SN", "FRB", "Other"]

# 初筛关键词 (仅用于 arXiv)
KEYWORDS_BROAD = [
    "black hole", "BHXB", "X-ray binary", "XRB", "microquasar", "AGN",
    "accretion", "transient", "outburst", "compact object", 'binary',
    'TDE', 'QPE', 'cataclysmic variables'
]

# 研究兴趣描述
RESEARCH_INTEREST = """
我的研究领域是：黑洞 X 射线双星 (BHXRB), AGN 以及相关的吸积物理。TDE, QPE 等近年来的热门领域也正在关注。
我主要关注观测类文章。
同时我们课题组有一台 1m 光学望远镜，光谱极限16等，测光极限21等，因此如果有能利用该望远镜的相关研究，也可以考虑。
我们也在尝试研究CV，因为可以充分利用光学观测资源。
"""

# 输出路径
POSTS_DIR = "./docs/posts"
ATELS_DIR = "./docs/atels"
STATE_FILE = os.path.join(ATELS_DIR, "state.json")

# ===========================================

def get_gemini_client():
    if "xxx" in API_KEY:
        raise ValueError("请设置有效的 GOOGLE_API_KEY")
    return genai.Client(api_key=API_KEY)

def clean_json_response(text):
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    return text.strip()

# --- ArXiv 逻辑 (严格保持您的原始逻辑) ---

def get_papers_by_date(target_date):
    print(f"[System] 正在检索日期为 {target_date} 的论文...")
    query = ' OR '.join([f'cat:{c}' for c in ARXIV_CATEGORIES])
    search = arxiv.Search(
        query=query,
        max_results=300,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    daily_papers = []
    client_arxiv = arxiv.Client(page_size=100, delay_seconds=3, num_retries=3)
    for result in client_arxiv.results(search):
        paper_date = result.published.date()
        if paper_date == target_date:
            daily_papers.append(result)
        elif paper_date < target_date:
            break
    return daily_papers

def keyword_pre_filter(papers):
    candidates = []
    for paper in papers:
        content = (paper.title + " " + paper.summary).lower()
        if any(k.lower() in content for k in KEYWORDS_BROAD):
            candidates.append(paper)
    return candidates

def ai_relevance_check(client, paper):
    prompt = f"""
    你是一位天体物理教授。请分析这篇论文与我研究兴趣的相关性。

    [我的研究兴趣]
    {RESEARCH_INTEREST}

    [论文信息]
    Title: {paper.title}
    Abstract: {paper.summary}

    请以 JSON 格式输出结果：
    - score: 0到10的整数
    - one_sentence_summary: 用中文一句话概括这篇论文做了什么（不超过50字）。
    - target_objects: 论文中提到的具体天体名称列表。

    只输出 JSON。
    """
    try:
        response = client.models.generate_content(model="gemini-3.1-flash-lite-preview", contents=prompt)
        return json.loads(clean_json_response(response.text))
    except:
        return {"score": 0, "one_sentence_summary": "分析失败", "target_objects": []}

def ai_summarize_short(client, paper, analysis_info):
    prompt = f"""
    请简要总结这篇论文。不要废话。

    Title: {paper.title}
    Abstract: {paper.summary}
    AI识别天体: {analysis_info.get('target_objects')}

    请用中文输出 Markdown，严格包含以下两点（总字数控制在 200 字以内）：
    1. **核心发现**: 发现了什么新现象或得出了什么新结论？
    2. **关键方法**: 也就是用了什么数据或什么模型。
    """
    try:
        response = client.models.generate_content(model="gemini-3.1-flash-lite-preview", contents=prompt)
        return response.text
    except Exception as e:
        return f"摘要生成失败: {e}"

def generate_obsidian_note(high_score_papers, low_score_papers, target_date):
    if not high_score_papers and not low_score_papers: return None
    high_score_papers.sort(key=lambda x: x['analysis']['score'], reverse=True)
    low_score_papers.sort(key=lambda x: x['analysis']['score'], reverse=True)
    date_str = target_date.strftime("%Y-%m-%d")
    file_name = f"Arxiv_Summary_{date_str}.md"
    file_path = os.path.join(POSTS_DIR, file_name)
    os.makedirs(POSTS_DIR, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"# arXiv Daily: {date_str}\n\n")
        f.write(f"## 重点关注 ({len(high_score_papers)}篇)\n")
        if not high_score_papers: f.write("今日无重点推荐。\n")
        for item in high_score_papers:
            paper, analysis, summary = item['paper'], item['analysis'], item['summary']
            f.write(f"### [{analysis['score']}] | [{paper.title}]({paper.entry_id})\n")
            f.write(f"**Authors**: {', '.join([a.name for a in paper.authors[:3]])} et al.\n\n")
            f.write(f"{summary}\n\n---\n")
        f.write(f"\n## 其他相关 ({len(low_score_papers)}篇)\n")
        for item in low_score_papers:
            paper, analysis = item['paper'], item['analysis']
            f.write(f"- **[{analysis['score']}]** [{paper.title}]({paper.entry_id})\n")
            f.write(f"  - *{analysis['one_sentence_summary']}*\n")
    return file_name

# --- ATel 逻辑 (排除干扰时间 + 精准提取) ---

def get_latest_atel_info_from_rss():
    import feedparser
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        resp = requests.get(ATEL_RSS_URL, headers=headers, timeout=30)
        feed = feedparser.parse(resp.text)
        return {int(e.link.split('=')[-1]): e for e in feed.entries}
    except: return {}

def fetch_atel_detail(atel_id):
    """从官网抓取完整信息，剔除当前时间干扰项"""
    url = f"{ATEL_BASE_URL}/?read={atel_id}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        wait_time = random.uniform(8, 15)
        print(f"  [Scraper] 正在抓取 ATel {atel_id} (等待 {wait_time:.1f}s)...")
        time.sleep(wait_time)
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # --- 核心改进：彻底移除“当前访问时间”标签 ---
        bad_time_div = soup.find(id='time')
        if bad_time_div:
            bad_time_div.decompose() # 从 DOM 树中彻底删除，防止被正则抓到
        
        # 1. 提取标题
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else f"ATel {atel_id}"
        if title.startswith(f"ATel {atel_id}: "): title = title.replace(f"ATel {atel_id}: ", "")

        # 2. 定向提取真正的发布日期
        date_str = "Unknown Date"
        # 使用分隔符获取纯文本，此时已不含 id='time' 的内容
        clean_text = soup.get_text(separator=' ')
        
        # 精准匹配发布时间格式：on [Date]; [Time] UT
        # 这个组合非常独特，不容易在正文中误触
        match = re.search(r'on\s+(\d{1,2}\s+[A-Za-z]{3,}\s+\d{4});\s+\d{2}:\d{2}\s+UT', clean_text)
        if match:
            date_str = match.group(1).strip() + " UT"
        else:
            # 备选匹配模式
            match_alt = re.search(r'(\d{1,2}\s+[A-Za-z]{3,}\s+\d{4}).*?UT', clean_text)
            if match_alt: date_str = match_alt.group(1).strip() + " UT"
        
        # 3. 提取正文
        content_div = soup.find('div', id='teltext')
        content = content_div.get_text(strip=True) if content_div else ""
        
        return {'id': atel_id, 'title': title, 'date': date_str, 'content': content, 'link': url}
    except Exception as e:
        print(f"[Error] 抓取 ATel {atel_id} 失败: {e}")
        return None

def ai_summarize_atel(client, atel):
    prompt = f"""
    分析 ATel 简报。研究兴趣：{RESEARCH_INTEREST}
    Title: {atel['title']}
    Content: {atel['content']}
    
    输出 JSON：
    - score: 0-10
    - object_name: 爆发源名称
    - classification: 从该列表中选择一个最合适的类别: {SOURCE_CATEGORIES}
    - source_type: 该天体性质描述（一句话）
    - telescopes: 使用的望远镜或卫星设备列表
    - one_sentence_summary: 中文一句话简述爆发
    - summary_md: 中文 Markdown (150字内)，必须包含：1. 核心观测现象；2. 望远镜/设备；3. 爆发性质，4. 建议我们做什么方面研究或用 1m 光学望远镜怎样做后随。
    
    只输出 JSON。
    """
    try:
        response = client.models.generate_content(model="gemini-3.1-flash-lite-preview", contents=prompt)
        return json.loads(clean_json_response(response.text))
    except: return None

# --- 存储与索引逻辑 ---

def get_iso_week(date_str: str):
    try:
        # 提取 "3 Mar 2026" 部分
        clean_date = date_str.split(';')[0].replace(' UT', '').strip()
        dt = datetime.datetime.strptime(clean_date, "%d %b %Y")
        year, week, _ = dt.isocalendar()
        return f"{year}-W{week:02d}"
    except:
        year, week, _ = datetime.datetime.now().isocalendar()
        return f"{year}-W{week:02d}"

def update_weekly_atel(new_items):
    os.makedirs(ATELS_DIR, exist_ok=True)
    weeks = {}
    for item in new_items:
        week = get_iso_week(item['obj']['date'])
        if week not in weeks: weeks[week] = []
        weeks[week].append(item)
    for week, items in weeks.items():
        file_path = os.path.join(ATELS_DIR, f"{week}.md")
        items.sort(key=lambda x: x['obj']['id'], reverse=True)
        new_block = ""
        for item in items:
            obj, ans = item['obj'], item['analysis']
            new_block += f"### [{ans['score']}] | [{obj['title']}]({obj['link']})\n"
            new_block += f"- **日期**: {obj['date']} | **源**: `{ans.get('object_name', 'Unknown')}`\n"
            new_block += f"- **设备**: {', '.join(ans.get('telescopes', []))}\n"
            new_block += f"- **概览**: {ans['one_sentence_summary']}\n\n{ans['summary_md']}\n\n---\n\n"
        old_content = ""
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                old_content = f.read()
                if f"# ATel Weekly: {week}" in old_content:
                    old_content = old_content.split("\n\n---\n\n", 1)[-1] if "\n\n---\n\n" in old_content else ""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# ATel Weekly: {week}\n\n" + new_block + old_content)

def update_source_atel(new_items):
    sources_dir = os.path.join(ATELS_DIR, "sources")
    os.makedirs(sources_dir, exist_ok=True)
    for item in new_items:
        obj, ans = item['obj'], item['analysis']
        source_name = ans.get('object_name', 'Unknown').strip().replace("/", "_").replace(" ", "_")
        if not source_name or source_name.lower() == 'unknown': continue
        file_path = os.path.join(sources_dir, f"{source_name}.md")
        entry = f"### ATel {obj['id']} | {obj['date']}\n**设备**: {', '.join(ans.get('telescopes', []))}\n\n{ans['summary_md']}\n\n---\n\n"
        content = ""
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if f"# Source: {source_name}" in content:
                    content = content.split("\n\n---\n\n", 1)[-1] if "\n\n---\n\n" in content else ""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# Source: {source_name}\n\n- **类别**: {ans.get('classification', 'Other')}\n- **简介**: {ans.get('source_type', '天文观测目标')}\n\n" + entry + content)

def update_atels_index():
    weekly_files = sorted([f for f in os.listdir(ATELS_DIR) if f.endswith(".md") and "-W" in f], reverse=True)
    sources_dir = os.path.join(ATELS_DIR, "sources")
    source_info_list = []
    if os.path.exists(sources_dir):
        for sf in os.listdir(sources_dir):
            if not sf.endswith(".md"): continue
            with open(os.path.join(sources_dir, sf), 'r', encoding='utf-8') as f:
                content = f.read()
                name = sf.replace(".md", "")
                cat_match = re.search(r'- \*\*类别\*\*: (.*)', content)
                intro_match = re.search(r'- \*\*简介\*\*: (.*)', content)
                date_match = re.search(r'### ATel \d+ \| (\d{1,2}\s+[A-Za-z]+\s+\d{4})', content)
                cat = cat_match.group(1).strip() if cat_match else "Other"
                intro = intro_match.group(1).strip() if intro_match else "暂无简介"
                latest_date_str = date_match.group(1).strip() if date_match else "01 Jan 1970"
                try: latest_dt = datetime.datetime.strptime(latest_date_str, "%d %b %Y")
                except: latest_dt = datetime.datetime(1970, 1, 1)
                source_info_list.append({'name': name, 'file': sf, 'cat': cat, 'intro': intro, 'date': latest_dt, 'date_str': latest_date_str})
    source_info_list.sort(key=lambda x: x['date'], reverse=True)
    with open(os.path.join(ATELS_DIR, "index.md"), 'w', encoding='utf-8') as f:
        f.write("# ATel 索引\n\n## 按周汇总\n")
        for wf in weekly_files: f.write(f"- [{wf.replace('.md', '')}]({wf})\n")
        f.write("\n## 爆发源追踪 (按更新日期排列)\n")
        for category in SOURCE_CATEGORIES:
            cat_items = [s for s in source_info_list if s['cat'] == category]
            if cat_items:
                f.write(f"\n### {category}\n")
                for item in cat_items:
                    f.write(f"- [{item['name']}](./sources/{item['file']}) | *{item['date_str']}* - {item['intro']}\n")

def update_home_page(arxiv_files):
    weekly_files = sorted([f for f in os.listdir(ATELS_DIR) if f.endswith(".md") and "-W" in f], reverse=True)
    atel_snippet = "暂无记录"
    if weekly_files:
        with open(os.path.join(ATELS_DIR, weekly_files[0]), 'r', encoding='utf-8') as f:
            lines = f.readlines()
            atel_snippet = "".join(lines[2:20]) + f"\n\n[查看本周完整 ATel](./atels/{weekly_files[0]})"
    with open("./docs/index.md", 'w', encoding='utf-8') as f:
        f.write("# ArXiv Daily Tracker\n\n## 最新天文简报 (ATel)\n\n" + atel_snippet + "\n\n[查看所有 ATel 索引](./atels/index.md)\n")
        f.write("\n---\n\n## 最新论文 (arXiv)\n")
        if arxiv_files:
            with open(os.path.join(POSTS_DIR, arxiv_files[0]), 'r', encoding='utf-8') as rf:
                f.write("".join(rf.readlines()[1:]))
            f.write(f"\n[查看历史目录](./posts/index.md)\n")
        else: f.write("今日无更新\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', type=str)
    parser.add_argument('--task', choices=['arxiv', 'atel', 'all'], default='all')
    args = parser.parse_args()
    client = get_gemini_client()

    if args.task in ['atel', 'all']:
        os.makedirs(ATELS_DIR, exist_ok=True)
        state = {'last_id': 0}
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f: state = json.load(f)
        rss_data = get_latest_atel_info_from_rss()
        max_rss_id = max(rss_data.keys()) if rss_data else state['last_id']
        
        new_atels = []
        for aid in range(state['last_id'] + 1, max_rss_id + 1):
            detail = fetch_atel_detail(aid)
            if not detail: continue
            print(f"  -> 分析 ATel {aid}: {detail['title'][:40]}...")
            ans = ai_summarize_atel(client, detail)
            if ans: new_atels.append({'obj': detail, 'analysis': ans})
        if new_atels:
            update_weekly_atel(new_atels)
            update_source_atel(new_atels)
            state['last_id'] = max_rss_id
            with open(STATE_FILE, 'w') as f: json.dump(state, f)
        update_atels_index()

    arxiv_files = []
    if args.task in ['arxiv', 'all']:
        target_date = datetime.datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else datetime.datetime.now(datetime.timezone.utc).date() - datetime.timedelta(days=1)
        raw_papers = get_papers_by_date(target_date)
        candidates = keyword_pre_filter(raw_papers)
        high_score, low_score = [], []
        for paper in candidates:
            analysis = ai_relevance_check(client, paper)
            score = analysis.get('score', 0)
            if score >= 6:
                summary = ai_summarize_short(client, paper, analysis)
                high_score.append({'paper': paper, 'analysis': analysis, 'summary': summary})
                time.sleep(12)
            else:
                low_score.append({'paper': paper, 'analysis': analysis})
                time.sleep(2)
        generate_obsidian_note(high_score, low_score, target_date)

    os.makedirs(POSTS_DIR, exist_ok=True)
    arxiv_files = sorted([f for f in os.listdir(POSTS_DIR) if f.startswith("Arxiv_Summary_") and f.endswith(".md")], reverse=True)
    update_home_page(arxiv_files)

if __name__ == "__main__":
    main()
