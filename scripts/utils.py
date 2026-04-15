"""
通用工具模块：日志系统、天体名称解析、日期处理。
"""
import os
import re
import json
import logging
import datetime

# ================= 日志系统 =================
def setup_logger(name: str = "arxiv_daily", level: int = logging.INFO) -> logging.Logger:
    """创建并返回统一格式的 Logger。"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger

logger = setup_logger()

# ================= SIMBAD 可选依赖 =================
try:
    from astroquery.simbad import Simbad
except ImportError:
    logger.warning("缺少 astroquery 库。SIMBAD 别名解析不可用。请运行: pip install astroquery")
    Simbad = None

# ================= 名称解析逻辑 =================
def normalize_source_name(name: str) -> str:
    """将天体名称归一化为大写无空格格式，用于比对。"""
    if not name:
        return ""
    name = re.sub(r'\(.*?\)', '', name)
    name = re.sub(r'^(SOURCE|OBJECT)[:\s]+', '', name, flags=re.IGNORECASE)
    return re.sub(r'[^A-Z0-9\+\-\._]', '', name.upper())


def get_aliases_from_simbad(primary_name: str) -> list[str]:
    """从 SIMBAD 数据库查询天体的所有已知别名。"""
    if not Simbad:
        return []
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
        logger.info(f"  [SIMBAD] 未找到 '{primary_name}' 的官方别名: {e}")
        return []


def get_canonical_name(name: str, aliases: list[str], source_map: dict) -> str:
    """
    根据名称和别名列表，在 source_map 中查找或注册规范名称。
    如果本地未命中，会尝试查询 SIMBAD 进行跨名称映射。
    """
    all_names = [name] + (aliases if aliases else [])

    def find_in_map(names):
        for n in names:
            norm = normalize_source_name(n)
            if norm and norm in source_map:
                return source_map[norm]
        return None

    result = find_in_map(all_names)
    if result:
        return result

    logger.info(f"  [SIMBAD] 正在为新源 '{name}' 拉取天文台标准别名以防重叠...")
    simbad_aliases = get_aliases_from_simbad(name)
    result = find_in_map(simbad_aliases)
    if result:
        norm = normalize_source_name(name)
        if norm:
            source_map[norm] = result
        return result

    new_canonical = name.strip().replace("/", "_").replace(" ", "_")
    for n in all_names + simbad_aliases:
        norm = normalize_source_name(n)
        if norm:
            source_map[norm] = new_canonical
    return new_canonical


def init_source_map_from_files(sources_dir: str) -> dict:
    """从已有的源文件名中重建 source_map。"""
    source_map = {}
    if not os.path.exists(sources_dir):
        return source_map
    for f in os.listdir(sources_dir):
        if not f.endswith(".md"):
            continue
        canonical = f.replace(".md", "")
        for n in canonical.split("___"):
            norm = normalize_source_name(n)
            if norm:
                source_map[norm] = canonical
    return source_map


# ================= 日期处理 =================
def get_iso_week(date_str: str) -> str:
    """将 ATel 日期字符串 (如 '12 Mar 2026 UT') 解析为 ISO 周格式 (如 '2026-W11')。"""
    try:
        m = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', date_str)
        if not m:
            return f"{datetime.datetime.now().isocalendar()[0]}-W{datetime.datetime.now().isocalendar()[1]:02d}"
        day, mon, year = m.group(1), m.group(2)[:3].capitalize(), m.group(3)
        clean_date = f"{day} {mon} {year}"
        dt = datetime.datetime.strptime(clean_date, '%d %b %Y')
        return f"{dt.isocalendar()[0]}-W{dt.isocalendar()[1]:02d}"
    except Exception as e:
        logger.warning(f"日期解析失败 '{date_str}': {e}")
        return f"{datetime.datetime.now().isocalendar()[0]}-W{datetime.datetime.now().isocalendar()[1]:02d}"
