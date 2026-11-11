from pathlib import Path
from lxml import html,etree
import json
D=Path(__file__).resolve().parents[1]/'dist';origin='https://www.rockbarfxxkup.com'
for lang,path,url in [(code,('index.html' if code=='en' else code.lower()+'/index.html'),origin+('/' if code=='en' else '/'+code.lower()+'/')) for code in ['en','ja','ko','th','zh-Hans']]:
 doc=html.fromstring((D/path).read_text());assert doc.get('lang')==lang
 assert len(doc.xpath('//h1'))==1
 assert doc.xpath('//link[@rel="canonical"]/@href')==[url]
 assert len(doc.xpath('//meta[@name="description"]'))==1
 assert len(doc.xpath('//meta[@property="og:image"]'))==1
 assert len(doc.xpath('//link[@hreflang]'))==6
 schema=json.loads(doc.xpath('//script[@type="application/ld+json"]/text()')[0]);bar=schema['@graph'][0]
 assert bar['@type']=='BarOrPub' and len(bar['openingHoursSpecification'])==2
 assert 'aggregateRating' not in bar
 for src in doc.xpath('//@src'):
  if src.startswith('/'):assert (D/src.lstrip('/')).exists(),src
 for attr in doc.xpath('//@data-en|//@data-ja'):assert 'data-ja=' not in attr
 assert 'muddyeagle18' not in (D/path).read_text()
 assert len(doc.xpath('//img[@width and @height]'))==len(doc.xpath('//img'))
 menu_path='/menu/' if lang=='en' else '/'+lang.lower()+'/menu/'
 assert doc.xpath(f'//a[@href="{menu_path}"]')
etree.fromstring((D/'sitemap.xml').read_bytes());assert 'Sitemap: '+origin+'/sitemap.xml' in (D/'robots.txt').read_text()
assert 'grayscale(' not in (D/'style.css').read_text()
print('PASS: canonical URLs, language alternates, metadata, schema, assets, sitemap and robots.')

# Reconcile each published inventory against its counter and structured data.
import runpy
whisky=runpy.run_path(str(D.parent/'scripts/build-whisky.py'))
for config in whisky['LANGUAGES']:
 inventory=whisky['parse_inventory'](config)
 expected=sum(len(group['items']) for group in inventory['groups'])
 page=D/config['folder']/'whisky/index.html'
 doc=html.fromstring(page.read_text())
 assert len(doc.xpath('//section[@data-category-id!="lottery"]//li[@class="whisky-item"]'))==expected
 assert str(expected) in doc.get_element_by_id('whisky-count').text_content()
 schema=json.loads(doc.xpath('//script[@type="application/ld+json"]/text()')[0])
 assert schema['mainEntity']['numberOfItems']==expected==len(schema['mainEntity']['itemListElement'])
 if config['code']=='en':
  assert doc.xpath('//title/text()')==doc.xpath('//h1/text()')==['Whiskey Bar in Sapporo’s Susukino | Rock Bar FxxK Up']
sitemap=etree.parse(str(D/'sitemap.xml'))
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9','x':'http://www.w3.org/1999/xhtml'}
homes={c:origin+('/' if c=='en' else '/'+c.lower()+'/') for c in ['en','ja','ko','th','zh-Hans']}
for url in homes.values():
 node=sitemap.xpath('//s:url[s:loc=$url]',namespaces=ns,url=url)[0]
 assert {a.get('hreflang'):a.get('href') for a in node.findall('x:link',ns)}==dict(homes,**{'x-default':homes['en']})
print('PASS: whisky inventory counts, English title/H1 and reciprocal homepage sitemap alternates.')
