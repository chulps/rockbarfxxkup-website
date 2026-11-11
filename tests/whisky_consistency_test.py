"""Read-only consistency checks for generated whisky and full-menu pages."""
import importlib.util
import json
import re
import unittest
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def load(name, path):
    spec=importlib.util.spec_from_file_location(name, ROOT/path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
w=load('whisky_builder','scripts/build-whisky.py')
m=load('menu_builder','scripts/build-menu.py')

def key(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', value).casefold() if c.isalnum())

class WhiskyConsistency(unittest.TestCase):
    def test_all_whisky_names_and_prices_match_the_full_menu(self):
        data=json.loads((ROOT/'source/menu/menu-data.json').read_text())
        index={key(item['name']):item for item in data}
        inventory=w.parse_inventory(w.LANGUAGES[0])
        self.assertEqual(sum(len(g['items']) for g in inventory['groups']),173)
        for group in inventory['groups']:
            for item in group['items']:
                self.assertIn(key(item['name']),index,item['name'])
                listed=m.price_label(index[key(item['name'])]['prices'])
                self.assertTrue(item['price'].startswith(listed),(item['name'],item['price'],listed))

    def test_locales_include_homepage_hours_and_contextual_menu_link(self):
        for config in w.LANGUAGES:
            code=config['code'];folder=config['folder'];base=ROOT/'dist'/folder
            page=(base/'whisky/index.html').read_text();menu=(base/'menu/index.html').read_text()
            facts=w.homepage_visit_facts(code)
            self.assertIn('21:00–03:00',page);self.assertIn('21:00–04:00',page)
            self.assertIn('064-0805',page);self.assertIn('¥500',page)
            self.assertIn(facts['hours_label'],page)
            route='/' + (folder+'/' if folder else '') + 'whisky/'
            self.assertIn('href="'+route+'" data-track-event="whisky_page_open"',menu)
            self.assertEqual(page.count('<p class="whisky-category-guide">'),19)
            for index in range(1,20):self.assertIn('id="category-'+str(index)+'"',page)
            self.assertEqual(len(re.findall(r'<li class="whisky-item"',page)),173)

if __name__=='__main__':unittest.main()
