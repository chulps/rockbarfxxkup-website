from pathlib import Path
from lxml import html, etree
from PIL import Image,ImageOps
import json,copy
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'dist';ORIGIN='https://www.rockbarfxxkup.com'
meta={
'en':('Rock Bar FxxK Up | Rock & Whisky in Susukino, Sapporo','Rock, whisky and a warm welcome in Susukino, Sapporo. Open from 21:00, about 4 minutes from Susukino Station. View our menu and find us on the 6th floor.'),
'ja':('Rock Bar FxxK Up｜札幌・すすきののロック＆ウイスキーバー','札幌・すすきの駅から徒歩約4分。ロックとウイスキーを楽しむRock Bar FxxK Up。毎晩21時オープン、第3旭観光ビル6階。メニュー・営業時間・アクセスはこちら。')}
meta.update({
'ko':('Rock Bar FxxK Up | 삿포로 스스키노 록 & 위스키 바','삿포로 스스키노의 록 & 위스키 바. 스스키노역에서 도보 약 4분, 매일 21:00 오픈. 메뉴와 영업시간을 확인하고 6층으로 오세요.'),
'th':('Rock Bar FxxK Up | บาร์ร็อกและวิสกี้ ซูซูกิโนะ ซัปโปโร','บาร์ร็อกและวิสกี้ในซูซูกิโนะ ซัปโปโร เดินจากสถานีซูซูกิโนะประมาณ 4 นาที เปิดทุกคืน 21:00 น. ดูเมนู เวลาเปิดปิด และเส้นทางมาชั้น 6'),
'zh-Hans':('Rock Bar FxxK Up｜札幌薄野摇滚与威士忌酒吧','札幌薄野的摇滚与威士忌酒吧，距薄野站步行约4分钟。每晚21:00营业，位于第3旭观光大楼6楼。查看菜单、营业时间和路线。')})
urls={code:ORIGIN+('/' if code=='en' else '/'+code.lower()+'/') for code in meta}
translations=json.loads((ROOT/'source/translations.json').read_text())
locales={'en':'en_US','ja':'ja_JP','ko':'ko_KR','th':'th_TH','zh-Hans':'zh_CN'}
base=html.document_fromstring((ROOT/'source/index.html').read_text())
# Use one real photograph for link previews, sized for social cards.
im=ImageOps.exif_transpose(Image.open(D/'assets/bottle-wall.jpg')).convert('RGB');ImageOps.fit(im,(1200,630)).save(D/'assets/social-preview.jpg',quality=88,optimize=True)
for code in meta:
 doc=copy.deepcopy(base);doc.set('lang',code);head=doc.find('head')
 for el in head.xpath('title|meta[@name="description"]|meta[starts-with(@property,"og:")]|meta[starts-with(@name,"twitter:")]|link[@rel="canonical"]|link[@rel="alternate"]'):head.remove(el)
 def tag(tag_name,**attrs):el=etree.SubElement(head,tag_name);el.attrib.update(attrs);return el
 title,desc=meta[code];tag('title').text=title
 tag('meta',name='description',content=desc)
 tag('meta',name='robots',content='index,follow,max-image-preview:large')
 tag('link',rel='canonical',href=urls[code])
 for lang,url in urls.items():tag('link',rel='alternate',hreflang=lang,href=url)
 tag('link',rel='alternate',hreflang='x-default',href=urls['en'])
 for key,val in {'type':'website','site_name':'Rock Bar FxxK Up','title':title,'description':desc,'url':urls[code],'locale':locales[code],'image':ORIGIN+'/assets/social-preview.jpg','image:secure_url':ORIGIN+'/assets/social-preview.jpg','image:width':'1200','image:height':'630','image:type':'image/jpeg','image:alt':'Whisky bottles behind the counter at Rock Bar FxxK Up, Sapporo'}.items():tag('meta',property='og:'+key,content=val)
 for other in meta:
  if other!=code:tag('meta',property='og:locale:alternate',content=locales[other])
 for key,val in {'card':'summary_large_image','title':title,'description':desc,'image':ORIGIN+'/assets/social-preview.jpg','image:alt':'Whisky bottles at Rock Bar FxxK Up in Susukino, Sapporo'}.items():tag('meta',name='twitter:'+key,content=val)
 tag('link',rel='manifest',href='/site.webmanifest');tag('link',rel='apple-touch-icon',href='/assets/apple-touch-icon.png')
 if code!='en':
  for el in doc.xpath('//*[@data-ja]'):
   for child in list(el):el.remove(child)
   el.text=None
   text=el.get('data-ja') if code=='ja' else translations[code][el.get('data-en')]
   fragments=html.fragments_fromstring(text)
   for frag in fragments:
    if isinstance(frag,str):
     if len(el):el[-1].tail=(el[-1].tail or '')+frag
     else:el.text=(el.text or '')+frag
    else:el.append(frag)
 # Root-relative assets work from every language URL.
 for el in doc.xpath('//*[@src or @href]'):
  for attr in ['src','href']:
   v=el.get(attr,'')
   if v.startswith('assets/') or v in ['style.css','app.js']:el.set(attr,'/'+v)
 for el in doc.xpath('//img'):
  src=el.get('src','');path=D/src.lstrip('/')
  if path.suffix.lower() in ['.jpg','.jpeg','.png'] and path.exists():
   w,h=Image.open(path).size;el.set('width',str(w));el.set('height',str(h));el.set('decoding','async')
 # Actual links expose the two fully translated pages to crawlers and visitors.
 nav=etree.SubElement(doc.find('body'),'nav',{'class':'language-links','aria-label':'Website languages'})
 for lang,label in [('en','English'),('ja','日本語'),('ko','한국어'),('th','ไทย'),('zh-Hans','简体中文')]:etree.SubElement(nav,'a',href=urls[lang],hreflang=lang,lang=lang).text=label
 schema={'@context':'https://schema.org','@graph':[
 {'@type':'BarOrPub','@id':ORIGIN+'/#bar','name':'Rock Bar FxxK Up','alternateName':['Rock Bar Fxxkup','ロックバー FxxK Up'],'url':ORIGIN+'/','image':[ORIGIN+'/assets/bottle-wall.jpg',ORIGIN+'/assets/neon-sign.jpg'],'logo':ORIGIN+'/assets/logo.svg','telephone':'+81-11-200-9666','address':{'@type':'PostalAddress','streetAddress':'第3旭観光ビル6F, 南5条西5丁目21-3','addressLocality':'札幌市中央区','addressRegion':'北海道','postalCode':'064-0805','addressCountry':'JP'},'hasMenu':'https://chulps.github.io/barticket-frontend/menu','hasMap':'https://maps.app.goo.gl/95hYVdZMdPot4WQy5','sameAs':['https://www.instagram.com/rockbar_fxxkup/'],'openingHoursSpecification':[{'@type':'OpeningHoursSpecification','dayOfWeek':['Monday','Wednesday'],'opens':'21:00','closes':'03:00'},{'@type':'OpeningHoursSpecification','dayOfWeek':['Tuesday','Thursday','Friday','Saturday','Sunday'],'opens':'21:00','closes':'04:00'}]},
 {'@type':'WebSite','@id':ORIGIN+'/#website','url':ORIGIN+'/','name':'Rock Bar FxxK Up','inLanguage':list(meta),'publisher':{'@id':ORIGIN+'/#bar'}},
 {'@type':'WebPage','@id':urls[code]+'#webpage','url':urls[code],'name':title,'description':desc,'inLanguage':code,'isPartOf':{'@id':ORIGIN+'/#website'},'about':{'@id':ORIGIN+'/#bar'}}]}
 tag('script',type='application/ld+json').text=json.dumps(schema,ensure_ascii=False).replace('</','<\\/')
 out=D/(code.lower()+'/index.html') if code!='en' else D/'index.html';out.parent.mkdir(exist_ok=True);out.write_text('<!doctype html>\n'+html.tostring(doc,encoding='unicode',method='html'))
(D/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+ORIGIN+'/sitemap.xml\n')
ns='http://www.sitemaps.org/schemas/sitemap/0.9';root=etree.Element('{'+ns+'}urlset',nsmap={None:ns})
for url in urls.values():el=etree.SubElement(root,'{'+ns+'}url');etree.SubElement(el,'{'+ns+'}loc').text=url
(D/'sitemap.xml').write_bytes(etree.tostring(root,xml_declaration=True,encoding='UTF-8',pretty_print=True))
(D/'site.webmanifest').write_text(json.dumps({'name':'Rock Bar FxxK Up — Sapporo','short_name':'FxxK Up','start_url':'/','display':'browser','background_color':'#161414','theme_color':'#161414','icons':[{'src':'/assets/apple-touch-icon.png','sizes':'180x180','type':'image/png'}]}))
# Use the existing logo, preserving the established brand.
logo=Image.open(D/'assets/logo.jpg').convert('RGB');ImageOps.pad(logo,(180,180),color='#161414').save(D/'assets/apple-touch-icon.png')
print('Built all five language pages, metadata, structured data, robots, sitemap, social image and icon.')
