"""Owner-approved category guide completeness and rendering regressions."""
import importlib.util
import json
import re
import unittest
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('whisky_builder', ROOT / 'scripts/build-whisky.py')
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)


class CategoryGuideTests(unittest.TestCase):
    def test_every_language_has_all_19_categories_and_intro_copy(self):
        names = {g['name'] for g in w.parse_inventory(w.LANGUAGES[0])['groups']}
        self.assertEqual(len(names), 19)
        self.assertEqual(set(w.CATEGORY_GUIDE), {l['code'] for l in w.LANGUAGES})
        for code, copy in w.CATEGORY_GUIDE.items():
            with self.subTest(language=code):
                self.assertEqual(set(copy['categories']), names)
                self.assertEqual(set(copy), {'philosophy_title', 'philosophy', 'start_title', 'start', 'japanese_note', 'lottery', 'categories'})
                for name, text in copy.items():
                    if name != 'categories':
                        self.assertTrue(isinstance(text, str) and text.strip())
                self.assertEqual(copy['lottery'].count('{price}'), 1)
                self.assertNotIn('¥1,000', copy['lottery'])
                if code != 'en':
                    for name, text in copy['categories'].items():
                        self.assertNotEqual(text, w.CATEGORY_GUIDE['en']['categories'][name])

    def test_approved_collective_voice_and_inventory_safe_edits(self):
        en = w.CATEGORY_GUIDE['en']
        self.assertIn('We might suggest a way to try it, or tell you how we like it', en['philosophy'])
        self.assertNotRegex(json.dumps(en, ensure_ascii=False), r'\bI(?:[ ’\']|\b)')
        self.assertIn('Sakurao Sherry Cask', en['categories']['Japanese Whisky — Other'])
        self.assertIn('Some Speyside whiskies also use peat.', en['categories']['Scotch — Speyside'])
        self.assertNotIn('Smoky Twelve', json.dumps(w.CATEGORY_GUIDE))
        self.assertIn('world blends', en['japanese_note'])

    def test_generated_pages_contain_each_guide_next_to_its_category(self):
        for cfg in w.LANGUAGES:
            code = cfg['code']
            copy = w.CATEGORY_GUIDE[code]
            html = (ROOT / 'dist' / cfg['folder'] / 'whisky/index.html').read_text()
            with self.subTest(language=code):
                self.assertEqual(html.count('<p class="whisky-category-guide">'), 19)
                self.assertEqual(html.count('data-whisky-japanese-note>'), 1)
                self.assertEqual(html.count('data-whisky-origin="japanese"'), 5)
                for idx, (name, text) in enumerate(copy['categories'].items(), 1):
                    section = re.search(r'<section class="whisky-category" data-whisky-group data-category-id="' + str(idx) + r'"[^>]*>(.*?)</section>', html, re.S)
                    self.assertIsNotNone(section)
                    self.assertIn('<p class="whisky-category-guide">' + escape(text) + '</p>', section[1])
                    self.assertLess(section[1].index('whisky-category-guide'), section[1].index('whisky-list'))
                for field in ['philosophy_title', 'philosophy', 'start_title', 'start', 'japanese_note']:
                    self.assertIn(escape(copy[field]), html)
                intro = html.index('<p class="whisky-intro">')
                philosophy = html.index('whisky-philosophy-title">')
                self.assertEqual(intro < philosophy, code == 'en')
                self.assertLess(html.rindex('<li class="whisky-item"'), html.index('id="category-lottery"'))
                self.assertLess(html.index('data-whisky-japanese-note>'), html.index('data-category-id="1"'))
                self.assertIn(escape(copy['lottery'].format(price='¥1,000')), html)
                self.assertNotIn('whisky-curated-guide', html)
                self.assertIn('<details class="whisky-start-guide"><summary>', html)
                self.assertEqual(html.count('<li class="whisky-item"'), sum(len(g['items']) for g in w.parse_inventory(cfg)['groups']))

    def test_compact_heading_beats_locale_homepage_heading_rules(self):
        css = (ROOT / "source/whisky-guide.css").read_text()
        self.assertIn(".whisky-page .whisky-philosophy h2{", css)
        self.assertIn("font:700 18px/1.4 var(--body);letter-spacing:0}", css)

    def test_incomplete_translation_fails_the_build_instead_of_falling_back(self):
        copy = w.CATEGORY_GUIDE['ja']['categories']
        name, value = next(iter(copy.items()))
        del copy[name]
        try:
            with self.assertRaisesRegex(ValueError, 'guide does not match'):
                w.render_page(w.LANGUAGES[1], w.parse_inventory(w.LANGUAGES[1]), {l['code']:w.page_url(l) for l in w.LANGUAGES})
        finally:
            copy[name] = value


if __name__ == '__main__':
    unittest.main()
