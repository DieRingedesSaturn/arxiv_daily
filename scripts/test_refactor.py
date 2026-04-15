"""
重构验证脚本：测试所有模块能否正常导入，核心工具函数是否正确。
"""
import sys

errors = []
passed = 0

# ========== 1. 导入测试 ==========
print("=" * 40)
print("模块导入测试")
print("=" * 40)

modules = [
    ("config", "from config import ARXIV_CATEGORIES, POSTS_DIR, ATELS_DIR"),
    ("utils", "from utils import logger, normalize_source_name, get_iso_week, get_canonical_name, init_source_map_from_files"),
    ("schemas", "from schemas import PaperEvaluation, ATelAnalysis, SourceAliases"),
    ("llm_api", "from llm_api import generate_content_with_retry"),
    ("arxiv_manager", "from arxiv_manager import get_new_arxiv_papers, keyword_pre_filter, ai_relevance_check, ai_summarize_short"),
    ("atel_manager", "from atel_manager import get_latest_atel_info_from_rss, fetch_atel_detail, ai_summarize_atel"),
    ("site_generator", "from site_generator import generate_obsidian_note, update_weekly_atel, update_source_atel, update_indexes"),
]

for name, stmt in modules:
    try:
        exec(stmt)
        print(f"  [OK] {name}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        errors.append(f"Import {name}: {e}")

# ========== 2. 工具函数测试 ==========
print("\n" + "=" * 40)
print("工具函数测试")
print("=" * 40)

# normalize_source_name
from utils import normalize_source_name, get_iso_week

test_cases_norm = [
    ("MAXI J1820+070", "MAXIJ1820+070"),
    ("  GRS 1915+105  ", "GRS1915+105"),
    ("(transient) Cyg X-1", "CYGX-1"),
    ("SOURCE: V404 Cyg", "V404CYG"),
    ("", ""),
]
for inp, expected in test_cases_norm:
    result = normalize_source_name(inp)
    if result == expected:
        print(f"  [OK] normalize('{inp}') = '{result}'")
        passed += 1
    else:
        msg = f"normalize('{inp}'): expected '{expected}', got '{result}'"
        print(f"  [FAIL] {msg}")
        errors.append(msg)

# get_iso_week
test_cases_week = [
    ("12 Mar 2026 UT", "2026-W11"),
    ("1 Jan 2026 UT", "2026-W01"),
    ("Unknown Date", None),  # should fallback to current week, just check it doesn't crash
]
for inp, expected in test_cases_week:
    result = get_iso_week(inp)
    if expected is None:
        # Just check it returns a valid format
        import re
        if re.match(r'\d{4}-W\d{2}', result):
            print(f"  [OK] get_iso_week('{inp}') = '{result}' (fallback)")
            passed += 1
        else:
            msg = f"get_iso_week('{inp}'): invalid format '{result}'"
            print(f"  [FAIL] {msg}")
            errors.append(msg)
    elif result == expected:
        print(f"  [OK] get_iso_week('{inp}') = '{result}'")
        passed += 1
    else:
        msg = f"get_iso_week('{inp}'): expected '{expected}', got '{result}'"
        print(f"  [FAIL] {msg}")
        errors.append(msg)

# ========== 3. main.py 入口测试 ==========
print("\n" + "=" * 40)
print("main.py 入口可导入性测试")
print("=" * 40)
try:
    import importlib
    main_mod = importlib.import_module("main")
    assert hasattr(main_mod, 'main')
    assert hasattr(main_mod, 'run_atel_task')
    assert hasattr(main_mod, 'run_arxiv_task')
    print(f"  [OK] main.py 可导入，包含 main/run_atel_task/run_arxiv_task")
    passed += 1
except Exception as e:
    print(f"  [FAIL] main.py: {e}")
    errors.append(f"main.py import: {e}")

# ========== 总结 ==========
print("\n" + "=" * 40)
total = passed + len(errors)
print(f"结果: {passed}/{total} 通过")
if errors:
    print("\n失败项:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("全部通过！")
    sys.exit(0)
