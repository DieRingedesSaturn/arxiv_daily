"""
ArXiv 论文获取、筛选与 AI 评估模块。
"""
from dataclasses import dataclass
import datetime
import re
import time
import xml.etree.ElementTree as ET

import arxiv
import requests

from config import (
    ARXIV_CATEGORIES, KEYWORDS_BROAD, RESEARCH_INTEREST,
    GEMINI_MODEL_LITE, GEMINI_MODEL_FLASH, PAID_MODEL,
)
from schemas import PaperEvaluation
from llm_api import generate_content_with_retry
from utils import logger


ARXIV_ATOM_BASE_URL = "https://rss.arxiv.org/atom"
ARXIV_REQUEST_INTERVAL_SECONDS = 3
ARXIV_USER_AGENT = (
    "arxiv_daily/1.0 "
    "(+https://github.com/DieRingedesSaturn/arxiv_daily)"
)


@dataclass(frozen=True)
class ArxivAuthor:
    """兼容 ``arxiv.Result.authors`` 的最小作者记录。"""

    name: str


@dataclass(frozen=True)
class ArxivPaper:
    """日报生成所需的 arXiv 论文元数据。"""

    entry_id: str
    title: str
    summary: str
    authors: list[ArxivAuthor]
    announcement_date: datetime.date


def _normalize_entry_id(entry_id: str) -> str:
    return entry_id.replace("http://", "https://")


def _clean_atom_summary(summary: str) -> str:
    """移除 arXiv Atom 日报在摘要前添加的公告头。"""
    return re.sub(
        r"^arXiv:\S+\s+Announce Type:\s*[^\n]+\s+Abstract:\s*",
        "",
        summary.strip(),
        count=1,
        flags=re.IGNORECASE,
    ).strip()


def parse_arxiv_atom_feed(xml_content: bytes | str) -> list[ArxivPaper]:
    """解析 arXiv 官方 Atom 日报，返回与现有处理链兼容的记录。"""
    root = ET.fromstring(xml_content)
    if not root.tag.endswith("feed"):
        raise ValueError("arXiv Atom 响应缺少 feed 根节点")

    namespaces = {
        "atom": "http://www.w3.org/2005/Atom",
        "dc": "http://purl.org/dc/elements/1.1/",
    }
    entries = root.findall("atom:entry", namespaces)
    papers = []

    for entry in entries:
        raw_id = (entry.findtext("atom:id", default="", namespaces=namespaces)).strip()
        title = (entry.findtext("atom:title", default="", namespaces=namespaces)).strip()
        summary = (entry.findtext("atom:summary", default="", namespaces=namespaces)).strip()
        published = (
            entry.findtext("atom:published", default="", namespaces=namespaces)
        ).strip()
        if not raw_id or not title or not summary or not published:
            logger.warning("arXiv Atom 条目缺少 id/title/summary/published，已跳过。")
            continue

        try:
            announcement_date = datetime.datetime.fromisoformat(
                published.replace("Z", "+00:00")
            ).date()
        except ValueError:
            logger.warning(f"arXiv Atom 条目的 published 日期无效: {published}")
            continue

        identifier = raw_id.rsplit(":", 1)[-1]
        creator = (
            entry.findtext("dc:creator", default="", namespaces=namespaces)
        ).strip()
        author_names = [name.strip() for name in creator.split(",") if name.strip()]
        authors = [ArxivAuthor(name) for name in author_names]
        if not authors:
            authors = [ArxivAuthor("作者未知")]

        papers.append(
            ArxivPaper(
                entry_id=f"https://arxiv.org/abs/{identifier}",
                title=" ".join(title.split()),
                summary=_clean_atom_summary(summary),
                authors=authors,
                announcement_date=announcement_date,
            )
        )

    if entries and not papers:
        raise ValueError("arXiv Atom 响应包含条目，但没有可用论文元数据")
    return papers


def _get_papers_from_atom(max_results: int) -> list[ArxivPaper]:
    categories = "+".join(ARXIV_CATEGORIES)
    url = f"{ARXIV_ATOM_BASE_URL}/{categories}"
    logger.info(f"正在从 arXiv 官方 Atom 日报获取: {categories}...")
    response = requests.get(
        url,
        headers={"User-Agent": ARXIV_USER_AGENT},
        timeout=30,
    )
    response.raise_for_status()
    return parse_arxiv_atom_feed(response.content)[:max_results]


def _run_search_api(query: str, max_results: int) -> list[arxiv.Result]:
    """以统一的限速配置执行一次 legacy search API 查询。"""
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )
    client = arxiv.Client(
        page_size=min(100, max_results),
        delay_seconds=3,
        num_retries=2,
    )
    return list(client.results(search))


def _get_papers_from_search_api(max_results: int) -> list[arxiv.Result]:
    """Atom 日报不可用时，使用低频、单层重试的搜索 API 回退。"""
    query = ' OR '.join([f'cat:{category}' for category in ARXIV_CATEGORIES])
    return _run_search_api(query, max_results)


def get_arxiv_papers_for_date(
    target_date: datetime.date,
    processed_ids: set[str],
    max_results: int = 200,
) -> list[arxiv.Result]:
    """按提交日期检索历史论文，用于 RSS 无法覆盖的人工回填。"""
    date_token = target_date.strftime("%Y%m%d")
    category_query = ' OR '.join(
        f'cat:{category}' for category in ARXIV_CATEGORIES
    )
    query = (
        f'({category_query}) AND '
        f'submittedDate:[{date_token}0000 TO {date_token}2359]'
    )
    logger.info(f"正在检索 arXiv 历史提交日期: {target_date}...")
    papers = _run_search_api(query, max_results)
    if len(papers) >= max_results:
        raise RuntimeError(
            f"{target_date} 的检索结果达到上限 {max_results}，"
            "为避免静默漏文，已中止本日回填。"
        )

    normalized_processed_ids = {
        _normalize_entry_id(entry_id) for entry_id in processed_ids
    }
    new_papers = [
        paper for paper in papers
        if _normalize_entry_id(paper.entry_id) not in normalized_processed_ids
    ]
    logger.info(
        f"arXiv 历史检索过滤后发现 {len(new_papers)} 篇未处理论文。"
    )
    return new_papers


# ================= 论文获取 =================
def get_new_arxiv_papers(
    processed_ids: set[str],
    max_results: int = 200,
) -> list[ArxivPaper | arxiv.Result]:
    """从每日 Atom feed 获取论文，不可用时回退到搜索 API。"""
    try:
        papers = _get_papers_from_atom(max_results)
        source = "Atom"
    except Exception as atom_error:
        logger.warning(
            f"arXiv Atom 日报获取失败 ({atom_error})，"
            "回退到搜索 API..."
        )
        # arXiv 对所有 legacy API（含 RSS）统一要求请求间隔至少 3 秒。
        time.sleep(ARXIV_REQUEST_INTERVAL_SECONDS)
        papers = _get_papers_from_search_api(max_results)
        source = "API"

    normalized_processed_ids = {
        _normalize_entry_id(entry_id) for entry_id in processed_ids
    }
    new_papers = [
        paper for paper in papers
        if _normalize_entry_id(paper.entry_id) not in normalized_processed_ids
    ]
    logger.info(
        f"arXiv {source} 过滤后发现 {len(new_papers)} 篇未处理的新论文。"
    )
    return new_papers



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
                model=PAID_MODEL, contents=prompt,
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
                    model=PAID_MODEL, contents=prompt,
                    max_retries=2, provider="openai",
                )
            except Exception as e3:
                return f"摘要生成失败: {e3}"
