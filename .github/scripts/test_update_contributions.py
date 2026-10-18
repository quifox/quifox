import importlib.util
import io
import json
import os
import tempfile
import unittest
import urllib.parse
from pathlib import Path
from unittest.mock import patch


spec = importlib.util.spec_from_file_location(
    "update_contributions", Path(__file__).with_name("update_contributions.py")
)
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class StaticStarsBadgeTests(unittest.TestCase):
    def test_readme_uses_static_badges_with_shields_number_format(self):
        cases = [
            (0, "0"),
            (999, "999"),
            (1000, "1k"),
            (1150, "1.1k"),
            (1250, "1.3k"),
            (3900, "3.9k"),
            (9950, "9.9k"),
            (9999, "10k"),
            (14180, "14k"),
            (14500, "15k"),
            (33000, "33k"),
            (999499, "999k"),
            (999500, "1M"),
            (1000000, "1M"),
            (1250000, "1.3M"),
        ]
        for stars, formatted in cases:
            with self.subTest(stars=stars), tempfile.TemporaryDirectory() as directory:
                readme = Path(directory) / "README.md"
                readme.write_text(
                    f"Before\n{updater.START}\nOld content\n{updater.END}\nAfter\n",
                    encoding="utf-8",
                )

                def respond(request, timeout):
                    url = urllib.parse.urlsplit(request.full_url)
                    if url.path == "/search/issues":
                        query = urllib.parse.parse_qs(url.query)["q"][0]
                        items = []
                        if "is:merged" in query.split():
                            items.append(
                                {
                                    "number": 42,
                                    "title": "Example contribution",
                                    "html_url": "https://github.com/example/project/pull/42",
                                    "repository_url": "https://api.github.com/repos/example/project",
                                    "pull_request": {"merged_at": "2026-10-18T00:00:00Z"},
                                }
                            )
                        data = {"items": items, "total_count": len(items)}
                    elif url.path == "/repos/example/project":
                        data = {"private": False, "stargazers_count": stars}
                    else:
                        self.fail(f"Unexpected external request: {request.full_url}")
                    return io.BytesIO(json.dumps(data).encode())

                with (
                    patch.dict(os.environ, GITHUB_USERNAME="quifox", GITHUB_TOKEN="test-token"),
                    patch.object(updater, "README_PATH", readme),
                    patch.object(updater.urllib.request, "urlopen", side_effect=respond),
                ):
                    updater.main()

                actual = readme.read_text(encoding="utf-8")
                self.assertIn(
                    f"[![Stars](https://img.shields.io/badge/stars-{formatted}-007ec6"
                    "?style=flat-square&logo=github)](https://github.com/example/project/stargazers)",
                    actual,
                )
                self.assertIn("contributions-1-8B5CF6?style=flat-square", actual)
                self.assertIn("[#42](https://github.com/example/project/pull/42)", actual)
                self.assertTrue(actual.startswith(f"Before\n{updater.START}\n"))
                self.assertTrue(actual.endswith(f"\n{updater.END}\nAfter\n"))


if __name__ == "__main__":
    unittest.main()
