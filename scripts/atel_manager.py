"""
ATel (Astronomer's Telegram) 获取、解析与 AI 分析模块。
"""
import re
import time
import random
import requests
import feedparser
from bs4 import BeautifulSoup

from config import (
    ATEL_BASE_URL, ATEL_RSS_URL, RESEARCH_INTEREST, GEMINI_MODEL_LITE,
)
from schemas import ATelAnalysis
from llm_api import generate_content_with_retry
from utils import logger


# ================= RSS 获取 =================
def get_latest_atel_info_from_rss() -> dict:
    """从 ATel RSS 获取最新条目的 {id: entry} 映射。"""
    try:
        resp = requests.get(ATEL_RSS_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
        return {int(e.link.split('=')[-1]): e for e in feed.entries}
    except requests.exceptions.RequestException as e:
        logger.error(f"获取 ATel RSS 失败: {e}")
        return {}
    except Exception as e:
        logger.error(f"解析 ATel RSS 失败: {e}")
        return {}


# ================= 详情抓取 =================
def fetch_atel_detail(atel_id: int) -> dict | None:
    """抓取单条 ATel 的详细信息（标题、日期、正文）。"""
    url = f"{ATEL_BASE_URL}/?read={atel_id}"
    try:
        wait_time = random.uniform(8, 15)
        logger.info(f"  [Scraper] 正在抓取 ATel {atel_id} (等待 {wait_time:.1f}s)...")
        time.sleep(wait_time)

        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        if soup.find(id='time'):
            soup.find(id='time').decompose()

        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else f"ATel {atel_id}"
        title = title.replace(f"ATel {atel_id}: ", "")

        # 提取日期
        full_text = soup.get_text(separator=' ')
        date_str = "Unknown Date"
        m = re.search(
            r'on\s+(\d{1,2}\s+[A-Za-z]{3,}\s+\d{4});\s+\d{2}:\d{2}\s+UT', full_text
        ) or re.search(r'(\d{1,2}\s+[A-Za-z]{3,}\s+\d{4}).*?UT', full_text)
        if m:
            date_str = m.group(1).strip() + " UT"

        # --- 正文提取逻辑 (三级回退) ---
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
                for sibling in subjects_div.find_next_siblings(['p', 'P']):
                    txt = sibling.get_text(strip=True)
                    if txt and "Tweet" not in txt and len(txt) > 5:
                        paragraphs.append(txt)
                content = "\n\n".join(paragraphs)

        # 3. 最后的保底方案：抓取所有较长的段落
        if not content:
            all_p = soup.find_all(['p', 'P'])
            content = "\n\n".join([
                p.get_text(strip=True) for p in all_p
                if len(p.get_text()) > 50 and "Tweet" not in p.get_text()
            ])

        return {'id': atel_id, 'title': title, 'date': date_str, 'content': content, 'link': url}
    except requests.exceptions.RequestException as e:
        logger.error(f"抓取 ATel {atel_id} 网络请求失败: {e}")
        return None
    except Exception as e:
        logger.error(f"抓取 ATel {atel_id} 失败: {e}")
        return None


# ================= AI 分析 =================
def ai_summarize_atel(atel: dict) -> dict | None:
    """使用 LLM 分析 ATel，提取核心信息并生成总结。"""
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
        return generate_content_with_retry(
            model=GEMINI_MODEL_LITE, contents=prompt,
            schema=ATelAnalysis, max_retries=3, base_delay=5, provider="google",
        )
    except Exception:
        logger.info("  [Fallback] ATel 免费 Lite 线路受限，尝试第三方付费 Lite 兜底...")
        try:
            return generate_content_with_retry(
                model=GEMINI_MODEL_LITE, contents=prompt,
                schema=ATelAnalysis, max_retries=2, provider="openai",
            )
        except Exception:
            return None
