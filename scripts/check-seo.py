from pathlib import Path
from lxml import html,etree
import json
D=Path(__file__).resolve().parents[1]/'dist';origin='https://www.rockbarfxxkup.com'
for lang,path,url in [('en','index.html',origin+'/'),('ja','ja/index.html',origin+'/ja/')]:
 doc=html.fromstring((D/path).read_text());assert doc.get('lang')==lang
 assert len(doc.xpath('//h1'))==1
 assert doc.xpath('//link[@rel="canonical"]/@href')==[url]
 assert len(doc.xpath('//meta[@name="description"]'))==1
 assert len(doc.xpath('//meta[@property="og:image"]'))==1
 assert len(doc.xpath('//link[@hreflang]'))==3
 schema=json.loads(doc.xpath('//script[@type="application/ld+json"]/text()')[0]);bar=schema['@graph'][0]
 assert bar['@type']=='BarOrPub' and len(bar['openingHoursSpecification'])==2
 assert 'aggregateRating' not in bar
 for src in doc.xpath('//@src'):
  if src.startswith('/'):assert (D/src.lstrip('/')).exists(),src
 for attr in doc.xpath('//@data-en|//@data-ja'):assert 'data-ja=' not in attr
 assert 'muddyeagle18' not in (D/path).read_text()
 assert len(doc.xpath('//img[@width and @height]'))==len(doc.xpath('//img'))
 assert doc.xpath('//a[@href="https://chulps.github.io/barticket-frontend/menu"]')
etree.fromstring((D/'sitemap.xml').read_bytes());assert 'Sitemap: '+origin+'/sitemap.xml' in (D/'robots.txt').read_text()
assert 'grayscale(' not in (D/'style.css').read_text()
print('PASS: canonical URLs, language alternates, metadata, schema, assets, sitemap and robots.')
