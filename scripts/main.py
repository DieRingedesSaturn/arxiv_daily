import os
import datetime
import json
import time
import pytz
import arxiv
import argparse
from google import genai
from google.genai import types

# ================= 配置区域 =================

# Google Gemini API Key
API_KEY = os.environ.get("GOOGLE_API_KEY", "xxx")

# arXiv 搜索配置
ARXIV_CATEGORIES = ["astro-ph.HE", "astro-ph.SR"]

# 初筛关键词
KEYWORDS_BROAD = [
    "black hole", "BHXB", "X-ray binary", "XRB", "microquasar", "AGN",
    "accretion", "transient", "outburst", "compact object", 'binary',
    'TDE', 'QPE', 'cataclysmic variables'
]

# 研究兴趣描述
RESEARCH_INTEREST = """
我的研究领域是：黑洞 X 射线双星 (BHXRB), AGN 以及相关的吸积物理。TDE, QPE 等近年来的热门领域也正在关注。
我主要关注观测类文章。
同时我们课题组有一台 1m 光学望远镜，因此如果有能利用该望远镜的相关研究，也可以考虑。
我们也在尝试研究CV，因为可以充分利用光学观测资源。
"""

# 输出路径
OUTPUT_DIR = "./docs/posts"

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

def get_papers_by_date(target_date):
    """
    检索指定日期的论文
    """
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
            
    print(f"[System] 原始检索到 {len(daily_papers)} 篇论文。")
    return daily_papers

def keyword_pre_filter(papers):
    candidates = []
    for paper in papers:
        content = (paper.title + " " + paper.summary).lower()
        if any(k.lower() in content for k in KEYWORDS_BROAD):
            candidates.append(paper)
    print(f"[Filter] 关键词初筛后剩余: {len(candidates)} 篇")
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
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=prompt
        )
        result_text = clean_json_response(response.text)
        return json.loads(result_text)
    except Exception as e:
        print(f"[Error] AI Filter 失败: {e}")
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
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"摘要生成失败: {e}"

def generate_obsidian_note(high_score_papers, low_score_papers, target_date):
    """
    将高分和低分论文分开展示，高分按评分排序
    """
    if not high_score_papers and not low_score_papers:
        print(f"[System] {target_date} 无相关论文。")
        return None

    # 按分数从高到低排序
    high_score_papers.sort(key=lambda x: x['analysis']['score'], reverse=True)
    low_score_papers.sort(key=lambda x: x['analysis']['score'], reverse=True)

    date_str = target_date.strftime("%Y-%m-%d")
    file_name = f"Arxiv_Summary_{date_str}.md"
    file_path = os.path.join(OUTPUT_DIR, file_name)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"# arXiv Daily: {date_str}\n\n")
        
        # === 第一部分：重点推荐 ===
        f.write(f"## 重点关注 ({len(high_score_papers)}篇)\n")
        if not high_score_papers:
            f.write("今日无重点推荐。\n")
        
        for item in high_score_papers:
            paper = item['paper']
            analysis = item['analysis']
            summary = item['summary']

            f.write(f"### [{analysis['score']}] | [{paper.title}]({paper.entry_id})\n")
            f.write(f"**Authors**: {', '.join([a.name for a in paper.authors[:3]])} et al.\n\n")
            f.write(f"{summary}\n\n")
            f.write("---\n")

        # === 第二部分：边缘相关 ===
        f.write(f"\n## 其他相关 ({len(low_score_papers)}篇)\n")
        f.write("（评分较低，但关键词匹配，建议快速扫读标题）\n\n")
        
        for item in low_score_papers:
            paper = item['paper']
            analysis = item['analysis']
            
            f.write(f"- **[{analysis['score']}]** [{paper.title}]({paper.entry_id})\n")
            f.write(f"  - *{analysis['one_sentence_summary']}*\n")

    print(f"[Success] 报告已生成: {file_path}")
    return file_name

def update_posts_index():
    files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith("Arxiv_Summary_") and f.endswith(".md")]
    files.sort(reverse=True)

    index_path = os.path.join(OUTPUT_DIR, "index.md")
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("# 日报目录\n\n")
        f.write("这里是按日期排列的所有 arXiv 每日简报：\n\n")
        
        for file_name in files:
            date_str = file_name.replace("Arxiv_Summary_", "").replace(".md", "")
            f.write(f"- [{date_str}]({file_name})\n")

    print(f"[System] 目录页已更新: {index_path}")
    return files

def update_home_page(files):
    if not files: return
    
    latest_file_name = files[0]
    latest_path = os.path.join(OUTPUT_DIR, latest_file_name)
    home_path = "./docs/index.md"
    
    with open(latest_path, 'r', encoding='utf-8') as f:
        latest_content = f.read()
    
    with open(home_path, 'w', encoding='utf-8') as f:
        f.write("# ArXiv Daily Tracker\n\n")
        f.write("> 专注于吸积、黑洞双星及相关高能物理领域的每日论文简报。\n\n")

        f.write("## 监控配置\n")
        f.write(f"- **arXiv 分类**: `{', '.join(ARXIV_CATEGORIES)}`\n")
        f.write(f"- **初筛关键词**: `{', '.join(KEYWORDS_BROAD)}`\n\n")
        
        f.write("## 近期日报\n")
        for f_name in files[:5]:
            date_str = f_name.replace("Arxiv_Summary_", "").replace(".md", "")
            f.write(f"- [{date_str}](./posts/{f_name}) ")
            if f_name == latest_file_name:
                f.write("*Latest*")
            f.write("\n")
        
        f.write("\n---\n\n")
        f.write("## 最新推送\n\n")
        f.write(latest_content)
        f.write("\n\n---\n[查看所有历史日报](./posts/index.md)\n")

    print(f"[System] 首页已更新，显示最新日报及配置信息。")

def main():
    parser = argparse.ArgumentParser(description='arXiv Daily Tracker')
    parser.add_argument('--date', type=str, help='指定日期 (格式: YYYY-MM-DD)，默认为昨天')
    args = parser.parse_args()

    if args.date:
        try:
            target_date = datetime.datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            print("[Error] 日期格式错误，请使用 YYYY-MM-DD")
            return
    else:
        # 默认仍为昨天
        target_date = datetime.datetime.now(datetime.timezone.utc).date() - datetime.timedelta(days=1)

    start_time = time.time()
    client = get_gemini_client()
    
    raw_papers = get_papers_by_date(target_date)
    if not raw_papers: 
        print(f"[System] {target_date} 没有找到原始论文。")
        update_posts_index()
        return
        
    candidates = keyword_pre_filter(raw_papers)
    if not candidates: 
        print(f"[System] {target_date} 关键词过滤后无剩余论文。")
        update_posts_index()
        return

    high_score_list = []
    low_score_list = []

    print(f"[System] 正在分析 {len(candidates)} 篇候选论文...")

    for paper in candidates:
        analysis = ai_relevance_check(client, paper)
        score = analysis.get('score', 0)
        print(f"  -> [{score}分] {paper.title[:30]}...")

        if score >= 6:
            summary = ai_summarize_short(client, paper, analysis)
            high_score_list.append({'paper': paper, 'analysis': analysis, 'summary': summary})
            time.sleep(12) 
        else:
            low_score_list.append({'paper': paper, 'analysis': analysis})
            time.sleep(2)

    generate_obsidian_note(high_score_list, low_score_list, target_date)
    files = update_posts_index()
    update_home_page(files)
    print(f"[System] 任务完成，耗时 {time.time() - start_time:.2f} 秒。")

if __name__ == "__main__":
    main()
