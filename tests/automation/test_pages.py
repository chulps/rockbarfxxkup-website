import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'automation'))
from site_pages import pages, ROOT, audit_page

class Coverage(unittest.TestCase):
    def test_all_fifteen_content_pages_and_privacy(self):
        items=pages()
        self.assertGreaterEqual(len(items),16)
        self.assertGreaterEqual(sum(p['route'].endswith('/music/') for p in items),5)
        self.assertIn('/privacy/',[p['route'] for p in items])
        for p in items:self.assertTrue(all(audit_page(p['path'].read_text(),p).values()),p['route'])
    def test_new_built_page_requires_sitemap_and_is_discovered(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);dist=root/'dist';dist.mkdir()
            (dist/'index.html').write_text('<html lang="en"></html>')
            xml='<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://www.rockbarfxxkup.com/</loc></url></urlset>'
            (dist/'sitemap.xml').write_text(xml)
            self.assertEqual(len(pages(root)),1)
            (dist/'new').mkdir();(dist/'new/index.html').write_text('<html lang="en"></html>')
            with self.assertRaisesRegex(ValueError,'mismatch'):pages(root)
            (dist/'sitemap.xml').write_text(xml.replace('</urlset>','<url><loc>https://www.rockbarfxxkup.com/new/</loc></url></urlset>'))
            self.assertEqual(len(pages(root)),2)
