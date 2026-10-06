from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.robots = []
        self.visible_text = []
        self.external_resources = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "meta" and attributes.get("name") == "robots":
            self.robots.append(attributes.get("content", ""))
        if tag in {"script", "iframe", "img", "style", "a"}:
            self.external_resources.append(tag)
        if tag == "link" and attributes.get("href") != "data:,":
            self.external_resources.append(tag)

    def handle_data(self, data):
        if data.strip():
            self.visible_text.append(data.strip())


class OfflineSiteTests(unittest.TestCase):
    def test_only_blank_nonindexable_pages_remain(self):
        pages = sorted(ROOT.rglob("*.html"))
        self.assertEqual([page.relative_to(ROOT).as_posix() for page in pages],
                         ["404.html", "index.html"])
        for page in pages:
            with self.subTest(page=page.name):
                parser = PageParser()
                parser.feed(page.read_text())
                self.assertEqual(parser.robots, ["noindex, nofollow, noarchive"])
                self.assertEqual(parser.visible_text, [])
                self.assertEqual(parser.external_resources, [])

    def test_crawlers_can_observe_noindex_and_missing_pages(self):
        self.assertEqual((ROOT / "robots.txt").read_text(),
                         "User-agent: *\nAllow: /\n")
        self.assertFalse((ROOT / "writing/index.html").exists())
        self.assertFalse((ROOT / "style.css").exists())

    def test_domain_and_static_hosting_are_preserved(self):
        self.assertEqual((ROOT / "CNAME").read_text().strip(), "brennandai.com")
        self.assertTrue((ROOT / ".nojekyll").exists())


if __name__ == "__main__":
    unittest.main()
