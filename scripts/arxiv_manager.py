"""
ArXiv 论文获取、筛选与 AI 评估模块。
"""
import time
import arxiv

from config import (
    ARXIV_CATEGORIES, KEYWORDS_BROAD, RESEARCH_INTEREST,
    GEMINI_MODEL_LITE, GEMINI_MODEL_FLASH,
)
from schemas import PaperEvaluation
from llm_api import generate_content_with_retry
from utils import logger


# ================= 论文获取 =================
def get_new_arxiv_papers(processed_ids: set[str], max_results: int = 200) -> list[arxiv.Result]:
    """从 arXiv API 获取最新论文，过滤已处理的 ID。"""
    logger.info(f"正在检索最新的 {max_results} 篇 arXiv 论文...")
    query = ' OR '.join([f'cat:{c}' for c in ARXIV_CATEGORIES])
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )
    client_arxiv = arxiv.Client(page_size=100, delay_seconds=10, num_retries=10)

    max_outer_retries = 3
    for attempt in range(max_outer_retries):
        try:
            new_papers = [
                res for res in client_arxiv.results(search)
                if res.entry_id.replace("http://", "https://") not in processed_ids
            ]
            logger.info(f"过滤后发现 {len(new_papers)} 篇未处理的新论文。")
            return new_papers
        except Exception as e:
            is_arxiv_error = "arxiv" in str(type(e)).lower()
            if is_arxiv_error:
                if attempt < max_outer_retries - 1:
                    wait_time = (attempt + 1) * 60
                    logger.warning(
                        f"arXiv API 请求失败 ({e})。正在进行第 {attempt+1} 次重试，等待 {wait_time} 秒..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"arXiv API 请求在 {max_outer_retries} 次尝试后仍然失败。")
                    raise
            else:
                raise
    return []


# ================= 关键词预筛 =================
def keyword_pre_filter(papers: list[arxiv.Result]) -> list[arxiv.Result]:
    """使用关键词列表对论文进行初步筛选。"""
    candidates = [
        p for p in papers
        if any(k.lower() in (p.title + " " + p.summary).lower() for k in KEYWORDS_BROAD)
    ]
    logger.info(f"关键词初筛后剩余: {len(candidates)} 篇")
    return candidates


# ================= AI 评估 =================
def ai_relevance_check(paper) -> dict:
    """使用 LLM 对论文进行相关性评分。"""
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
        return generate_content_with_retry(
            model=GEMINI_MODEL_LITE, contents=prompt,
            schema=PaperEvaluation, provider="google", max_retries=3,
        )
    except Exception:
        logger.info("  [Fallback] 免费 Lite 打分拥堵，切换付费 Lite...")
        try:
            return generate_content_with_retry(
                model=GEMINI_MODEL_LITE, contents=prompt,
                schema=PaperEvaluation, provider="openai", max_retries=2,
            )
        except Exception:
            return {"score": 0, "one_sentence_summary": "解析失败", "target_objects": []}


def ai_summarize_short(paper, analysis_info: dict) -> str:
    """使用 LLM 为高分论文生成中文三段式摘要。"""
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
        return generate_content_with_retry(
            model=GEMINI_MODEL_FLASH, contents=prompt,
            max_retries=2, base_delay=2, provider="google",
        )
    except Exception:
        logger.info("  [Fallback 1] 免费 Flash 失败，降级免费 Lite...")
        try:
            return generate_content_with_retry(
                model=GEMINI_MODEL_LITE, contents=prompt,
                max_retries=2, base_delay=2, provider="google",
            )
        except Exception:
            logger.info("  [Fallback 2] 免费路线全挂，启用第三方付费 lite 兜底...")
            try:
                return generate_content_with_retry(
                    model=GEMINI_MODEL_LITE, contents=prompt,
                    max_retries=2, provider="openai",
                )
            except Exception as e3:
                return f"摘要生成失败: {e3}"
