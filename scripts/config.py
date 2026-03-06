import os

# ================= 环境变量配置 =================
# 默认首选引擎，优先使用免费 Google API
API_PROVIDER = os.environ.get("API_PROVIDER", "google").lower()

# 双端密钥分离管理
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.ohmygpt.com/v1")

# ================= 模型配置 =================
GEMINI_MODEL_FLASH = "gemini-3-flash-preview"
GEMINI_MODEL_LITE = "gemini-3.1-flash-lite-preview"

# ================= 天文检索配置 =================
ARXIV_CATEGORIES = ["astro-ph.HE", "astro-ph.SR"]
ATEL_BASE_URL = "https://www.astronomerstelegram.org"
ATEL_RSS_URL = f"{ATEL_BASE_URL}/?rss"

SOURCE_CATEGORIES = ["BHXRB", "NSXRB", "CV", "AGN", "TDE", "QPE", "GRB", "SN", "FRB", "Other"]

KEYWORDS_BROAD = [
    "black hole", "black holes", "bhxb", "x-ray binary", "x-ray binaries", "xrb", "microquasar", 'binaries',
    "agn", "active galactic nucle", 
    "cataclysmic variable", "cataclysmic variables", "cvs",
    "accretion", "jet", "outburst", "transient", "tde", "tidal disruption", "qpe"
]

RESEARCH_INTEREST = """
【核心研究领域】黑洞X射线双星 (BHXRB) 与 活动星系核 (AGN) 的吸积与喷流物理，侧重于能谱分析 (spectral analysis)、时变分析 (timing analysis) 以及多波段联合观测。
【重点拓展领域】潮汐撕裂事件 (TDE)、准周期爆发 (QPE) 以及亮红新星 (LRN) 等涉及吸积机制与双星相互作用的新兴暂现源物理。
【观测设备与落地能力】
1. 我们课题组拥有一台 1m 光学望远镜 (北纬40度，光谱极限16等，测光极限21等)。如果论文或爆发源涉及激变变星 (CV) 或其他适合该望远镜跟进的目标，可以考虑。
2. 我们熟练使用且可申请的空间/地面设备包括：SVOM, Insight-HXMT, Einstein Probe (EP), Swift, XMM-Newton, ESO光学望远镜, LCO，并期望拓展射电观测。
"""

# ================= 输出路径配置 =================
POSTS_DIR = "./docs/posts"
ATELS_DIR = "./docs/atels"
STATE_FILE = os.path.join(ATELS_DIR, "state.json")
ARXIV_STATE_FILE = os.path.join(POSTS_DIR, "state.json")
SOURCE_MAP_FILE = os.path.join(ATELS_DIR, "source_aliases.json")