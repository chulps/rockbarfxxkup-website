from pathlib import Path
from lxml import html, etree
import subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='1a1c106b8eba6fc99d6b2c642123dfdbcd036224'
D=ROOT/'dist'
for path in ['dist/analytics.js','dist/experiments.js','dist/app.js','source/experiments.json']:
 assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT),path
notices=[('ja','お酒は20歳になってから。飲酒運転は法律で禁止されています。'),('en','Alcohol is for ages 20 and over. Never drink and drive.')]
paths=['index.html','ja/index.html','ko/index.html','th/index.html','zh-hans/index.html','privacy/index.html']
for path in paths:
 doc=html.fromstring((D/path).read_text())
 assert len(doc.xpath('//script[contains(@src,"googletagmanager.com/gtag/js")]'))==1
 assert len(doc.xpath('//script[@src="/analytics.js"]'))==1
 assert 'allow_google_signals:false,allow_ad_personalization_signals:false' in (D/path).read_text()
 for lang,notice in notices:
  assert doc.xpath('//footer//p[@lang=$lang and text()=$notice]',lang=lang,notice=notice)
 assert len(doc.xpath('//footer//a[starts-with(@href,"/privacy/")]'))==1
 for a in doc.xpath('//a[starts-with(@href,"/")]'):
  target=a.get('href').split('#')[0]
  if target.endswith('/'):target+='index.html'
  assert (D/target.lstrip('/')).is_file(),(path,target)
policy=html.fromstring((D/'privacy/index.html').read_text())
assert policy.xpath('//link[@rel="canonical"]/@href')==['https://www.rockbarfxxkup.com/privacy/']
assert policy.xpath('//section[@id="en" and @lang="en"]') and policy.xpath('//section[@id="ja" and @lang="ja"]')
assert not policy.xpath('//script[@data-site-module="experiments"]|//script[@src="/app.js"]|//form')
assert 'window.FXXKUP_EXPERIMENT_CONFIG' not in (D/'privacy/index.html').read_text()
assert len(policy.xpath('//h1'))==1
assert policy.xpath('//title/text()') and policy.xpath('//meta[@name="description"]/@content')
locs=etree.parse(str(D/'sitemap.xml')).xpath('//*[local-name()="loc"]/text()')
assert len(locs)==6 and len(set(locs))==6 and 'https://www.rockbarfxxkup.com/privacy/' in locs
print('PASS: 6 pages have bilingual notices, linked policy, one GA4 install; policy metadata and sitemap valid; tracking/runtime/config unchanged byte-for-byte from v28.')
