import importlib
import datetime
import json
import sys
import types
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


def _load_main_with_stubbed_dependencies():
    arxiv_manager = types.ModuleType("arxiv_manager")
    for name in (
        "get_new_arxiv_papers",
        "get_arxiv_papers_for_date",
        "keyword_pre_filter",
        "ai_relevance_check",
        "ai_summarize_short",
    ):
        setattr(arxiv_manager, name, Mock())

    atel_manager = types.ModuleType("atel_manager")
    for name in (
        "get_latest_atel_info_from_rss",
        "fetch_atel_detail",
        "ai_summarize_atel",
    ):
        setattr(atel_manager, name, Mock())

    site_generator = types.ModuleType("site_generator")
    for name in (
        "generate_obsidian_note",
        "update_weekly_atel",
        "update_source_atel",
        "update_indexes",
    ):
        setattr(site_generator, name, Mock())

    stubs = {
        "arxiv_manager": arxiv_manager,
        "atel_manager": atel_manager,
        "site_generator": site_generator,
    }
    with patch.dict(sys.modules, stubs):
        sys.modules.pop("main", None)
        return importlib.import_module("main")


def _detail(atel_id):
    return {
        "id": atel_id,
        "title": f"ATel {atel_id}",
        "date": "28 Jul 2026 UT",
        "content": "content",
        "link": f"https://example.test/{atel_id}",
    }


def _analysis(atel_id):
    return {
        "score": 8,
        "object_name": f"Source {atel_id}",
        "classification": "Other",
        "aliases": [],
        "summary_md": "summary",
    }


class ATelRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.main = _load_main_with_stubbed_dependencies()

    def test_failed_id_is_retried_without_reprocessing_later_successes(self):
        with TemporaryDirectory() as tmp:
            state_file = Path(tmp) / "state.json"
            state_file.write_text('{"last_id": 10}', encoding="utf-8")

            fetch = Mock(side_effect=lambda aid: None if aid == 12 else _detail(aid))
            analyze = Mock(side_effect=lambda item: _analysis(item["id"]))

            with (
                patch.object(self.main, "STATE_FILE", str(state_file)),
                patch.object(self.main, "ATELS_DIR", tmp),
                patch.object(
                    self.main,
                    "get_latest_atel_info_from_rss",
                    return_value={11: object(), 12: object(), 13: object()},
                ),
                patch.object(self.main, "fetch_atel_detail", fetch),
                patch.object(self.main, "ai_summarize_atel", analyze),
                patch.object(self.main.time, "sleep"),
            ):
                self.main.run_atel_task()

            state = json.loads(state_file.read_text(encoding="utf-8"))
            self.assertEqual(state, {"last_id": 13, "pending_ids": [12]})
            written_ids = [
                item["obj"]["id"]
                for item in self.main.update_weekly_atel.call_args.args[0]
            ]
            self.assertEqual(written_ids, [11, 13])

            self.main.update_weekly_atel.reset_mock()
            fetch.reset_mock(side_effect=True)
            fetch.side_effect = lambda aid: _detail(aid)

            with (
                patch.object(self.main, "STATE_FILE", str(state_file)),
                patch.object(self.main, "ATELS_DIR", tmp),
                patch.object(
                    self.main,
                    "get_latest_atel_info_from_rss",
                    return_value={},
                ),
                patch.object(self.main, "fetch_atel_detail", fetch),
                patch.object(self.main, "ai_summarize_atel", analyze),
                patch.object(self.main.time, "sleep"),
            ):
                self.main.run_atel_task()

            state = json.loads(state_file.read_text(encoding="utf-8"))
            self.assertEqual(state, {"last_id": 13, "pending_ids": []})
            fetch.assert_called_once_with(12)

    def test_analysis_failure_is_kept_for_retry(self):
        with TemporaryDirectory() as tmp:
            state_file = Path(tmp) / "state.json"
            state_file.write_text('{"last_id": 20}', encoding="utf-8")

            with (
                patch.object(self.main, "STATE_FILE", str(state_file)),
                patch.object(self.main, "ATELS_DIR", tmp),
                patch.object(
                    self.main,
                    "get_latest_atel_info_from_rss",
                    return_value={21: object()},
                ),
                patch.object(
                    self.main,
                    "fetch_atel_detail",
                    return_value=_detail(21),
                ),
                patch.object(self.main, "ai_summarize_atel", return_value=None),
                patch.object(self.main.time, "sleep"),
            ):
                self.main.run_atel_task()

            state = json.loads(state_file.read_text(encoding="utf-8"))
            self.assertEqual(state, {"last_id": 21, "pending_ids": [21]})
            self.main.update_weekly_atel.assert_not_called()


class ArxivDateTests(unittest.TestCase):
    def setUp(self):
        self.main = _load_main_with_stubbed_dependencies()

    def test_feed_announcement_date_is_used_by_default(self):
        papers = [
            types.SimpleNamespace(
                announcement_date=datetime.date(2026, 8, 10),
            ),
            types.SimpleNamespace(
                announcement_date=datetime.date(2026, 8, 10),
            ),
        ]
        self.assertEqual(
            self.main._resolve_arxiv_target_date(papers),
            datetime.date(2026, 8, 10),
        )

    def test_explicit_date_overrides_feed_date(self):
        requested = datetime.date(2026, 8, 9)
        papers = [
            types.SimpleNamespace(
                announcement_date=datetime.date(2026, 8, 10),
            )
        ]
        self.assertEqual(
            self.main._resolve_arxiv_target_date(papers, requested),
            requested,
        )

    def test_mixed_feed_dates_are_rejected(self):
        papers = [
            types.SimpleNamespace(
                announcement_date=datetime.date(2026, 8, 9),
            ),
            types.SimpleNamespace(
                announcement_date=datetime.date(2026, 8, 10),
            ),
        ]
        with self.assertRaisesRegex(ValueError, "多个公告日期"):
            self.main._resolve_arxiv_target_date(papers)

    def test_backfill_range_is_inclusive(self):
        self.assertEqual(
            list(
                self.main._iter_date_range(
                    datetime.date(2026, 8, 2),
                    datetime.date(2026, 8, 4),
                )
            ),
            [
                datetime.date(2026, 8, 2),
                datetime.date(2026, 8, 3),
                datetime.date(2026, 8, 4),
            ],
        )

    def test_backfill_skips_existing_daily_file(self):
        with TemporaryDirectory() as tmp:
            existing = Path(tmp) / "Arxiv_Summary_2026-08-02.md"
            existing.write_text("manual", encoding="utf-8")
            with (
                patch.object(self.main, "POSTS_DIR", tmp),
                patch.object(self.main, "run_arxiv_task") as run,
                patch.object(self.main.time, "sleep"),
            ):
                self.main.run_arxiv_backfill(
                    datetime.date(2026, 8, 2),
                    datetime.date(2026, 8, 3),
                )

            run.assert_called_once_with(
                target_date=datetime.date(2026, 8, 3),
                backfill_date=datetime.date(2026, 8, 3),
            )


class ATelIdempotencyTests(unittest.TestCase):
    def test_weekly_file_does_not_duplicate_an_existing_atel(self):
        import site_generator

        item = {"obj": _detail(30), "analysis": _analysis(30)}
        with TemporaryDirectory() as tmp, patch.object(
            site_generator, "ATELS_DIR", tmp
        ):
            site_generator.update_weekly_atel([item])
            site_generator.update_weekly_atel([item])

            weekly = Path(tmp) / "2026-W31.md"
            content = weekly.read_text(encoding="utf-8")
            self.assertEqual(content.count("ATel 30:"), 1)

    def test_source_file_does_not_duplicate_an_existing_atel(self):
        import site_generator

        item = {"obj": _detail(31), "analysis": _analysis(31)}
        with TemporaryDirectory() as tmp:
            atels_dir = Path(tmp)
            source_map = atels_dir / "source_aliases.json"
            with (
                patch.object(site_generator, "ATELS_DIR", str(atels_dir)),
                patch.object(
                    site_generator,
                    "SOURCE_MAP_FILE",
                    str(source_map),
                ),
                patch.object(
                    site_generator,
                    "get_canonical_name",
                    return_value="Source_31",
                ),
            ):
                site_generator.update_source_atel([item])
                site_generator.update_source_atel([item])

            source_file = atels_dir / "sources" / "Source_31.md"
            content = source_file.read_text(encoding="utf-8")
            self.assertEqual(content.count("ATel 31:"), 1)


if __name__ == "__main__":
    unittest.main()
