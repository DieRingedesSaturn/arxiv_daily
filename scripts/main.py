import os
import datetime
import json
import time
import pytz
import arxiv
from google import genai
from google.genai import types

# ================= 配置区域 =================

# Google Gemini API Key
API_KEY = os.environ.get("GOOGLE_API_KEY", "xxx")

# arXiv 搜索配置
ARXIV_CATEGORIES = ["astro-ph.HE"]

# 初筛关键词
KEYWORDS_BROAD = [
    "black hole", "BHXB", "X-ray binary", "XRB", "microquasar",
    "accretion", "transient", "outburst", "compact object"
]

# 研究兴趣描述
RESEARCH_INTEREST = """
我的研究领域是：黑洞 X 射线双星 (BHXRB), AGN 以及相关的吸积物理。
我特别关注观测类文章，以及关于吸积盘、喷流耦合的物理模型。
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

def get_papers_by_date():
    target_date = datetime.datetime.now(datetime.timezone.utc).date()
    target_date = target_date - datetime.timedelta(days=1) # 获取昨天的（适配时区）
    
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
    """
    修改点：让 AI 在分析相关性的同时，顺便写好一句话总结。
    这样低分论文就不需要二次调用 API，节省时间。
    """
    prompt = f"""
    你是一位天体物理学助手。请分析这篇论文与我研究兴趣的相关性。

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
            model="gemini-3.1-flash-lite-preview", # 建议用 flash 模型，速度快
            contents=prompt
        )
        result_text = clean_json_response(response.text)
        return json.loads(result_text)
    except Exception as e:
        print(f"[Error] AI Filter 失败: {e}")
        return {"score": 0, "one_sentence_summary": "分析失败", "target_objects": []}

def ai_summarize_short(client, paper, analysis_info):
    """
    修改点：针对高分论文的精简总结。
    """
    prompt = f"""
    请简要总结这篇论文。基于摘要即可，不要废话。

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

def generate_obsidian_note(high_score_papers, low_score_papers):
    """
    修改点：将高分和低分论文分开展示
    """
    if not high_score_papers and not low_score_papers:
        print("[System] 今日无相关论文。")
        return

    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(OUTPUT_DIR, f"Arxiv_Summary_{today_str}.md")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"## arXiv Daily: {today_str}\n\n")
        
        # === 第一部分：重点推荐 ===
        f.write(f"### 重点关注 ({len(high_score_papers)}篇)\n")
        if not high_score_papers:
            f.write("今日无重点推荐。\n")
        
        for item in high_score_papers:
            paper = item['paper']
            analysis = item['analysis']
            summary = item['summary']

            f.write(f"#### {analysis['score']} ⭐ | {paper.title}\n")
            f.write(f"**Authors**: {', '.join([a.name for a in paper.authors[:3]])} et al.\n\n")
            f.write(f"{summary}\n\n") # 这里是精简后的总结
            f.write(f"[arXiv]({paper.entry_id})\n")
            f.write("---\n")

        # === 第二部分：边缘相关（仅列表）===
        f.write(f"\n### 其他相关 ({len(low_score_papers)}篇)\n")
        f.write("（评分较低，但关键词匹配，建议快速扫读标题）\n\n")
        
        for item in low_score_papers:
            paper = item['paper']
            analysis = item['analysis']
            
            # 低分论文只显示一行：[分数] 标题 - 一句话总结
            f.write(f"- **[{analysis['score']}]** [{paper.title}]({paper.entry_id})\n")
            f.write(f"  - *{analysis['one_sentence_summary']}*\n")

    print(f"[Success] 报告已生成: {file_path}")

def main():
    start_time = time.time()
    client = get_gemini_client()
    
    # 获取与初筛
    raw_papers = get_papers_by_date()
    if not raw_papers: return
    candidates = keyword_pre_filter(raw_papers)
    if not candidates: return

    high_score_list = []
    low_score_list = []

    print(f"[System] 正在分析 {len(candidates)} 篇候选论文...")

    for paper in candidates:
        # 1. 分析与打分 (同时获取一句话总结)
        analysis = ai_relevance_check(client, paper)
        score = analysis.get('score', 0)
        
        print(f"  -> [{score}分] {paper.title[:30]}...")

        # 2. 分流处理
        if score >= 6:
            # 高分：生成精简总结
            summary = ai_summarize_short(client, paper, analysis)
            high_score_list.append({
                'paper': paper,
                'analysis': analysis,
                'summary': summary
            })
            time.sleep(15) # 避免限流
        else:
            # 低分：直接存入列表，使用 analysis 中的 one_sentence_summary
            low_score_list.append({
                'paper': paper,
                'analysis': analysis
            })
            time.sleep(2) # 稍微快一点，因为只调了一次 API

    # 生成报告
    generate_obsidian_note(high_score_list, low_score_list)
    print(f"[System] 任务完成，耗时 {time.time() - start_time:.2f} 秒。")

if __name__ == "__main__":
    main()