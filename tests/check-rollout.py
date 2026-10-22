from pathlib import Path
from lxml import html
import json,subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='cb5c17e6758df33097b4795c8a4a2159457481d5'
def byclass(doc,name): return doc.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," '+name+' ")]')
def text(el): return ' '.join(el.text_content().split())
config=json.loads((ROOT/'source/experiments.json').read_text())
assert config['firstVisit']['enabled'] is True
assert not (ROOT/'dist/__qa__').exists(), 'Temporary QA fixtures must never be packaged'
for lang,path in [('en','index.html'),('ja','ja/index.html'),('ko','ko/index.html'),('th','th/index.html'),('zh-Hans','zh-hans/index.html')]:
 old=html.fromstring(subprocess.check_output(['git','show',f'{BASE}:dist/{path}'],cwd=ROOT).decode())
 new=html.fromstring((ROOT/'dist'/path).read_text())
 assert new.get('data-directions-version')=='B' and new.get('data-footer-version')=='B'
 assert not byclass(new,'experiment-copy-a') and not byclass(new,'footer-copy-a')
 assert text(byclass(old,'experiment-copy-b')[0])==text(byclass(new,'experiment-copy-b')[0])
 assert [text(e) for e in byclass(old,'footer-copy-b')]==[text(e) for e in byclass(new,'footer-copy-b')]
 assert sorted(old.xpath('//a/@href'))==sorted(new.xpath('//a/@href'))
 for section in ['hero-line','hero-desc','about','drinks','nights','visit','social-links']:
  assert [text(e) for e in byclass(old,section)]==[text(e) for e in byclass(new,section)],(lang,section)
 for a in new.xpath('//a[contains(@href,"maps.app.goo.gl") or contains(@href,"instagram.com") or starts-with(@href,"tel:")]'):
  assert a.get('data-track-event') and a.get('data-track-placement')
 raw=(ROOT/'dist'/path).read_text()
 assert 'window.siteExperiment=' not in raw and 'window.footerExperiment=' not in raw
 gate=new.xpath('//script[@data-site-module="experiments"]/text()')[0]
 assert gate.index('config.enabled !== true') < gate.index('localStorage')
 assert new.xpath('//script[@data-site-module="experiments"]')
 assert new.xpath('//script[@src="/analytics.js"]')
 assert 'first_visit_confidence_2026_10_v1' in raw and '"enabled": true' in raw
print('PASS: all 5 static B pages match v26 B copy, original hero control, information, destinations and action tracking; confidence test enabled.')
