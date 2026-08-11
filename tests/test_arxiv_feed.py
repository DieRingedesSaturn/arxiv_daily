import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


ATOM_SAMPLE = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:dc="http://purl.org/dc/elements/1.1/">
  <id>http://rss.arxiv.org/atom/astro-ph.HE+astro-ph.SR</id>
  <entry>
    <id>oai:arXiv.org:2608.06453v1</id>
    <title>  A title\n      with spacing  </title>
    <summary>arXiv:2608.06453v1 Announce Type: new
Abstract: First abstract.</summary>
    <published>2026-08-10T00:00:00-04:00</published>
    <dc:creator>Alice Example, Bob Example</dc:creator>
  </entry>
  <entry>
    <id>oai:arXiv.org:2608.06461v2</id>
    <title>Second title</title>
    <summary>arXiv:2608.06461v2 Announce Type: replace
Abstract: Second abstract.</summary>
    <published>2026-08-10T00:00:00-04:00</published>
    <dc:creator>Carol Example</dc:creator>
  </entry>
</feed>
"""


def _load_arxiv_manager():
    fake_arxiv = types.ModuleType("arxiv")
    fake_arxiv.Result = type("Result", (), {})
    fake_arxiv.SortCriterion = types.SimpleNamespace(SubmittedDate="submitted")
    fake_arxiv.Search = Mock()
    fake_arxiv.Client = Mock()

    fake_schemas = types.ModuleType("schemas")
    fake_schemas.PaperEvaluation = type("PaperEvaluation", (), {})

    fake_llm_api = types.ModuleType("llm_api")
    fake_llm_api.generate_content_with_retry = Mock()

    module_name = "arxiv_manager_under_test"
    spec = importlib.util.spec_from_file_location(
        module_name,
        SCRIPTS_DIR / "arxiv_manager.py",
    )
    module = importlib.util.module_from_spec(spec)
    stubs = {
        module_name: module,
        "arxiv": fake_arxiv,
        "schemas": fake_schemas,
        "llm_api": fake_llm_api,
    }
    with patch.dict(sys.modules, stubs):
        spec.loader.exec_module(module)
    return module


class ArxivAtomTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manager = _load_arxiv_manager()

    def test_parse_atom_feed_produces_pipeline_compatible_papers(self):
        papers = self.manager.parse_arxiv_atom_feed(ATOM_SAMPLE)

        self.assertEqual(len(papers), 2)
        self.assertEqual(
            papers[0].entry_id,
            "https://arxiv.org/abs/2608.06453v1",
        )
        self.assertEqual(papers[0].title, "A title with spacing")
        self.assertEqual(papers[0].summary, "First abstract.")
        self.assertEqual(
            [author.name for author in papers[0].authors],
            ["Alice Example", "Bob Example"],
        )
        self.assertEqual(str(papers[0].announcement_date), "2026-08-10")
        self.assertEqual(papers[1].summary, "Second abstract.")

    def test_primary_atom_path_filters_processed_ids(self):
        papers = self.manager.parse_arxiv_atom_feed(ATOM_SAMPLE)
        with (
            patch.object(
                self.manager,
                "_get_papers_from_atom",
                return_value=papers,
            ) as atom_fetch,
            patch.object(self.manager, "_get_papers_from_search_api") as api_fetch,
        ):
            result = self.manager.get_new_arxiv_papers(
                {"http://arxiv.org/abs/2608.06453v1"},
                max_results=50,
            )

        self.assertEqual(
            [paper.entry_id for paper in result],
            ["https://arxiv.org/abs/2608.06461v2"],
        )
        atom_fetch.assert_called_once_with(50)
        api_fetch.assert_not_called()

    def test_search_api_is_used_only_when_atom_fails(self):
        papers = self.manager.parse_arxiv_atom_feed(ATOM_SAMPLE)
        with (
            patch.object(
                self.manager,
                "_get_papers_from_atom",
                side_effect=RuntimeError("feed unavailable"),
            ),
            patch.object(
                self.manager,
                "_get_papers_from_search_api",
                return_value=papers,
            ) as api_fetch,
            patch.object(self.manager.time, "sleep") as sleep,
        ):
            result = self.manager.get_new_arxiv_papers(set(), max_results=20)

        self.assertEqual(len(result), 2)
        sleep.assert_called_once_with(3)
        api_fetch.assert_called_once_with(20)

    def test_empty_daily_feed_is_valid(self):
        empty_feed = (
            b'<feed xmlns="http://www.w3.org/2005/Atom">'
            b'<id>http://rss.arxiv.org/atom/astro-ph.HE</id></feed>'
        )
        self.assertEqual(self.manager.parse_arxiv_atom_feed(empty_feed), [])

    def test_search_api_fallback_has_single_bounded_retry_layer(self):
        client_instance = Mock()
        client_instance.results.return_value = iter([])
        with (
            patch.object(self.manager.arxiv, "Search", return_value=object()),
            patch.object(
                self.manager.arxiv,
                "Client",
                return_value=client_instance,
            ) as client,
        ):
            result = self.manager._get_papers_from_search_api(200)

        self.assertEqual(result, [])
        client.assert_called_once_with(
            page_size=100,
            delay_seconds=3,
            num_retries=2,
        )

    def test_historical_fetch_scopes_query_and_filters_processed_ids(self):
        first = types.SimpleNamespace(
            entry_id="https://arxiv.org/abs/2608.00001v1"
        )
        second = types.SimpleNamespace(
            entry_id="https://arxiv.org/abs/2608.00002v1"
        )
        with patch.object(
            self.manager,
            "_run_search_api",
            return_value=[first, second],
        ) as search:
            result = self.manager.get_arxiv_papers_for_date(
                __import__("datetime").date(2026, 8, 4),
                {"http://arxiv.org/abs/2608.00001v1"},
                max_results=50,
            )

        self.assertEqual(result, [second])
        query = search.call_args.args[0]
        self.assertIn("cat:astro-ph.HE OR cat:astro-ph.SR", query)
        self.assertIn(
            "submittedDate:[202608040000 TO 202608042359]",
            query,
        )
        search.assert_called_once_with(query, 50)

    def test_historical_fetch_refuses_possible_truncation(self):
        papers = [
            types.SimpleNamespace(entry_id=f"https://arxiv.org/abs/{index}")
            for index in range(2)
        ]
        with patch.object(
            self.manager,
            "_run_search_api",
            return_value=papers,
        ):
            with self.assertRaisesRegex(RuntimeError, "静默漏文"):
                self.manager.get_arxiv_papers_for_date(
                    __import__("datetime").date(2026, 8, 4),
                    set(),
                    max_results=2,
                )


if __name__ == "__main__":
    unittest.main()
