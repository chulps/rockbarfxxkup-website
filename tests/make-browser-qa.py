"""Temporary local-browser fixtures. MUST be removed before packaging."""
from pathlib import Path
from lxml import html,etree
import json
root=Path(__file__).resolve().parents[1]
for lang,route in [('en',''),('ja','ja/'),('ko','ko/'),('th','th/'),('zh-Hans','zh-hans/')]:
 for mode in ['rollout','next-a','next-b']:
  doc=html.document_fromstring((root/'dist'/route/'index.html').read_text())
  head=doc.find('head')
  for script in list(head.findall('script')):
   if 'googletagmanager' in script.get('src','') or "gtag('config'" in (script.text or ''):head.remove(script)
  mock=etree.Element('script');mock.text="window.gtag=function(command,event,params){if(command!=='event')return;let el=document.getElementById('qa-events');if(!el){el=document.createElement('pre');el.id='qa-events';el.setAttribute('aria-label','QA event capture');el.style.cssText='white-space:pre-wrap;padding:24px;background:#fff;color:#111;position:relative;z-index:99';document.body.append(el)}el.textContent+=JSON.stringify({event,...params})+'\\n'};"
  head.insert(0,mock)
  if mode!='rollout':
   config=next(s for s in head.findall('script') if 'window.FXXKUP_EXPERIMENT_CONFIG=' in (s.text or ''))
   value=json.loads(config.text.split('=',1)[1].rstrip(';'));value['firstVisit']['enabled']=True
   config.text='window.FXXKUP_EXPERIMENT_CONFIG='+json.dumps(value,ensure_ascii=False)+';localStorage.setItem('+json.dumps(value['firstVisit']['storageKey'])+','+json.dumps(mode[-1].upper())+');'
  for a in doc.xpath('//a[starts-with(@href,"http")]'):a.set('target','_blank');a.set('rel','noopener')
  dest=root/'dist'/'__qa__'/mode/lang/'index.html';dest.parent.mkdir(parents=True,exist_ok=True)
  dest.write_text('<!doctype html>\n'+html.tostring(doc,encoding='unicode'))
print('Created 15 isolated fixtures with GA4 network loading removed. Remove dist/__qa__ before packaging.')
