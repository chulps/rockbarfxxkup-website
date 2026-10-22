from pathlib import Path
from lxml import html, etree
from PIL import Image,ImageOps
import json,copy
from io import BytesIO
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
experiments=json.loads((ROOT/'source/experiments.json').read_text())
locales={'en':'en_US','ja':'ja_JP','ko':'ko_KR','th':'th_TH','zh-Hans':'zh_CN'}
base=html.document_fromstring((ROOT/'source/index.html').read_text())
# Use one real photograph for link previews, sized for social cards.
im=ImageOps.exif_transpose(Image.open(D/'assets/neon-sign.jpg')).convert('RGB');ImageOps.fit(im,(1200,630)).save(D/'assets/neon-social-preview.jpg',quality=88,optimize=True)
# Responsive WebP derivatives preserve originals for metadata and future edits.
image_variants={}
for image_path in (D/'assets').glob('*.jpg'):
 if image_path.stem in ['social-preview','neon-social-preview','logo']:continue
 image=ImageOps.exif_transpose(Image.open(image_path)).convert('RGB')
 widths=sorted(set([min(w,image.width) for w in [400,720,768,960,1108,image.width]]))
 variants=[]
 for width in widths:
  target=D/'assets'/f'{image_path.stem}-{width}.webp'
  resized=image.resize((width,round(image.height*width/image.width)),Image.Resampling.LANCZOS)
  buffer=BytesIO();resized.save(buffer,'WEBP',quality=82,method=6);target.write_bytes(buffer.getvalue())
  variants.append((width,'/assets/'+target.name))
 image_variants[image_path.name]=variants
for code in meta:
 doc=copy.deepcopy(base);doc.set('lang',code);head=doc.find('head')
 # Inline the small site stylesheet; font CSS is nonblocking and locale-specific.
 for link in head.xpath('link[@rel="stylesheet"]'):
  if link.get('href') in ['style.css','/style.css']:head.remove(link)
  elif 'fonts.googleapis.com' in link.get('href',''):
   families='family=Barlow+Condensed:wght@600;700;800&family=DM+Sans:wght@400;500;600;700'
   if code=='ja':families+='&family=Noto+Sans+JP:wght@400;600;800'
   href='https://fonts.googleapis.com/css2?'+families+'&display=swap'
   link.set('href',href);link.set('rel','preload');link.set('as','style');link.set('onload',"this.onload=null;this.rel='stylesheet'")
   fallback=etree.SubElement(head,'noscript');etree.SubElement(fallback,'link',rel='stylesheet',href=href)
 style=etree.SubElement(head,'style');style.text=(D/'style.css').read_text()

 labels={
 'en':['Language','Website language','Inside FxxK Up','Previous photo','Next photo','Skip to content','Main navigation','Choose a photo','Filter drinks'],
 'ja':['言語','表示言語','FxxK Upの店内','前の写真','次の写真','本文へ移動','メインナビゲーション','写真を選ぶ','ドリンクの絞り込み'],
 'ko':['언어','웹사이트 언어','FxxK Up 내부','이전 사진','다음 사진','본문으로 이동','주 메뉴','사진 선택','음료 필터'],
 'th':['ภาษา','ภาษาของเว็บไซต์','ภายใน FxxK Up','ภาพก่อนหน้า','ภาพถัดไป','ข้ามไปยังเนื้อหา','เมนูหลัก','เลือกภาพ','กรองเครื่องดื่ม'],
 'zh-Hans':['语言','网站语言','FxxK Up 店内','上一张','下一张','跳至正文','主导航','选择照片','筛选饮品']}[code]
 doc.get_element_by_id('language').text=labels[0]
 doc.xpath('//*[@class="language-options"]')[0].set('aria-label',labels[1])
 for a in doc.xpath('//*[@data-language]'):
  if a.get('data-language')==code:a.set('aria-current','page')
 for el in doc.xpath('//*[@aria-label]'):
  original=el.get('aria-label')
  mapping=dict(zip(['Inside FxxK Up','Previous photo','Next photo','Main navigation','Choose a photo','Filter drinks'],[labels[2],labels[3],labels[4],labels[6],labels[7],labels[8]]))
  if original in mapping:el.set('aria-label',mapping[original])
 doc.xpath('//*[@class="skip"]')[0].text=labels[5]

 for el in head.xpath('title|meta[@name="description"]|meta[starts-with(@property,"og:")]|meta[starts-with(@name,"twitter:")]|link[@rel="canonical"]|link[@rel="alternate"]'):head.remove(el)
 def tag(tag_name,**attrs):el=etree.SubElement(head,tag_name);el.attrib.update(attrs);return el
 title,desc=meta[code];tag('title').text=title
 # One GA4 installation per page; disable advertising personalization features.
 tag('script').text="window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-JPYT9JRWBT',{allow_google_signals:false,allow_ad_personalization_signals:false});"
 # Previous winners are static HTML. Preserve old browser keys and GA4 history,
 # but do not assign or emit new exposure events for either retired test.
 # The independent next test stays disabled until a separately approved launch.
 tag('script').text='window.FXXKUP_EXPERIMENT_CONFIG='+json.dumps(experiments,ensure_ascii=False).replace('</','<\\/')+';'
 # Inline this tiny gate so a disabled future test adds no blocking request.
 module=tag('script');module.set('data-site-module','experiments')
 module.text=(D/'experiments.js').read_text().replace('</','<\\/')
 ga=tag('script',src='https://www.googletagmanager.com/gtag/js?id=G-JPYT9JRWBT');ga.set('async','')
 events=tag('script',src='/analytics.js');events.set('defer','')

 tag('meta',name='description',content=desc)
 tag('meta',name='robots',content='index,follow,max-image-preview:large')
 tag('link',rel='canonical',href=urls[code])
 for lang,url in urls.items():tag('link',rel='alternate',hreflang=lang,href=url)
 tag('link',rel='alternate',hreflang='x-default',href=urls['en'])
 for key,val in {'type':'website','site_name':'Rock Bar FxxK Up','title':title,'description':desc,'url':urls[code],'locale':locales[code],'image':ORIGIN+'/assets/neon-social-preview.jpg','image:secure_url':ORIGIN+'/assets/neon-social-preview.jpg','image:width':'1200','image:height':'630','image:type':'image/jpeg','image:alt':'Red FxxK Up neon sign at the bar in Sapporo'}.items():tag('meta',property='og:'+key,content=val)
 for other in meta:
  if other!=code:tag('meta',property='og:locale:alternate',content=locales[other])
 for key,val in {'card':'summary_large_image','title':title,'description':desc,'image':ORIGIN+'/assets/neon-social-preview.jpg','image:alt':'Red FxxK Up neon sign in Susukino, Sapporo'}.items():tag('meta',name='twitter:'+key,content=val)
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
   if path.name in image_variants:
    variants=image_variants[path.name]
    el.set('src',variants[-1][1]);el.set('srcset',', '.join(f'{url} {width}w' for width,url in variants))
    is_hero='hero-photo' in el.getparent().get('class','')
    el.set('sizes','(max-width: 700px) 100vw, 44vw' if is_hero else '(max-width: 374px) 88vw, (max-width: 700px) 42vw, (max-width: 1100px) 44vw, 21vw')

 # Actual links expose the two fully translated pages to crawlers and visitors.
 nav=etree.SubElement(doc.find('body'),'nav',{'class':'language-links','aria-label':'Website languages'})
 for lang,label in [('en','English'),('ja','日本語'),('ko','한국어'),('th','ไทย'),('zh-Hans','简体中文')]:etree.SubElement(nav,'a',href=urls[lang],hreflang=lang,lang=lang).text=label
 # Stable action names across languages; no visitor-entered data is collected.
 for link in doc.xpath('//a[@href]'):
  href=link.get('href');classes=link.get('class','').split();event=None
  if link.get('data-language') or link.get('hreflang'):
   event='language_select'
   if not link.get('data-language'):link.set('data-language',link.get('hreflang'))
  elif href=='https://chulps.github.io/barticket-frontend/menu':event='menu_open'
  elif href.startswith('tel:'):event='phone_click'
  elif 'maps.app.goo.gl/' in href:event='google_reviews_click' if 'rating' in classes else 'directions_click'
  elif 'instagram.com/' in href:
   event='instagram_click'
   link.set('data-track-destination','chuck' if '/chakkufxxkupu/' in href else 'bar')
  elif href=='#visit':event='find_us_click'
  if event:
   link.set('data-track-event',event)
   placement=link.get('data-track-placement')
   if not placement:
    placement='content'
    for ancestor in link.iterancestors():
     if 'mobile-bar' in ancestor.get('class','').split():placement='mobile_bar';break
     if ancestor.tag in ['header','footer']:placement=ancestor.tag;break
     if ancestor.tag=='section':placement=ancestor.get('id') or 'social';break
     if 'language-links' in ancestor.get('class','').split():placement='language_links';break
   link.set('data-track-placement',placement)
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
