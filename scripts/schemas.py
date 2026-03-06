from pydantic import BaseModel, Field
from config import SOURCE_CATEGORIES

class SourceAliases(BaseModel):
    aliases: list[str] = Field(description="爆发源的所有常见天文别名列表。若无，返回空列表。")

class PaperEvaluation(BaseModel):
    score: int = Field(description="0到10的整数。10分代表极其契合课题组研究领域。")
    one_sentence_summary: str = Field(description="中文一句话概括论文核心内容，不超过50字。")
    target_objects: list[str] = Field(description="明确提到的具体天体名称或编号列表。若无，返回空列表。")

class ATelAnalysis(BaseModel):
    score: int = Field(description="0到10的整数，表示与研究兴趣的相关性。")
    object_name: str = Field(description="爆发源的首选名称 (如 MAXI J1820+070)。如果未提及，返回 'Unknown'。")
    aliases: list[str] = Field(description="仅从当前 ATel 原文中提取该爆发源的其他别名或巡天编号。若无则返回空列表。禁止自行编造。")
    classification: str = Field(description=f"从该列表中选择一个最合适的类别: {', '.join(SOURCE_CATEGORIES)}。")
    summary_md: str = Field(description="""中文精简总结(约150字)。禁止使用Markdown标题。
请严格包含以下两部分，使用加粗作为引导：
**爆发速递**: (用几句话讲清谁用什么设备发现了什么现象)
**观测短评**: (是否有光学后随价值以及能否用我们的望远镜观测。是否有申请其他设备观测的必要。)""")