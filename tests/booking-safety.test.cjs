const { test } = require('node:test');
// These tests exercise the live form and are retained for restoration. Booking is currently hidden.
const bookingTest = test.skip;
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { webcrypto } = require('node:crypto');
const { TextEncoder } = require('node:util');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
bookingTest('localized placeholders and language labels survive generation', () => {
  const labels = {en:'Website language',ja:'ウェブサイトの言語',ko:'웹사이트 언어',th:'ภาษาเว็บไซต์','zh-hans':'网站语言'};
  for (const [locale, label] of Object.entries(labels)) {
    const dir = locale === 'en' ? '' : locale + '/';
    const html = fs.readFileSync(path.join(root, 'dist', dir, 'book/index.html'), 'utf8');
    assert.ok(html.includes('class="language-links" aria-label="' + label + '"'), locale);
    assert.doesNotMatch(html, /name="note_language"/, locale);
    assert.match(html, /name="translate_note"/, locale);
    for (const key of ['namePlaceholder', 'emailPlaceholder', 'notePlaceholder']) {
      const tag = html.match(new RegExp('<(?:input|textarea)\\b[^>]*data-copy-placeholder="' + key + '"[^>]*>'));
      assert.ok(tag, `${locale}: ${key} key`);
      assert.match(tag[0], /(?:^|\s)placeholder="[^"]+"/, `${locale}: ${key} value`);
    }
  }
});
bookingTest('localized booking pages load the shared brand fonts', () => {
  for (const locale of ['en', 'ja', 'ko', 'th', 'zh-hans']) {
    const dir = locale === 'en' ? '' : locale + '/';
    const html = fs.readFileSync(path.join(root, 'dist', dir, 'book/index.html'), 'utf8');
    assert.match(html, /fonts\.googleapis\.com\/css2\?family=Barlow\+Condensed[^" ]*family=DM\+Sans[^" ]*family=Noto\+Sans\+JP/);
    assert.match(html, /rel="preload" as="style" onload="this\.onload=null;this\.rel='stylesheet'"/);
    assert.match(html, /<noscript><link rel="stylesheet" href="https:\/\/fonts\.googleapis\.com\/css2\?/);
  }
});
bookingTest('localized pages keep fields and submit disabled without initialization', () => {
  for (const locale of ['en', 'ja', 'ko', 'th', 'zh-hans']) {
    const dir = locale === 'en' ? '' : locale + '/';
    const html = fs.readFileSync(path.join(root, 'dist', dir, 'book/index.html'), 'utf8');
    assert.match(html, /<noscript><p class="booking-note"[^>]*>[^<]+<\/p><\/noscript>/);
    assert.match(html, /<fieldset id="booking-controls" disabled>[\s\S]*name="guest_name"[\s\S]*name="contact_email"[\s\S]*name="note"[\s\S]*id="submit-button"[^>]*disabled[\s\S]*<\/fieldset>/);
    const home = fs.readFileSync(path.join(root, 'dist', dir, 'index.html'), 'utf8');
    const href = locale === 'en' ? '/book/' : '/' + locale + '/book/';
    assert.ok(home.includes('href="' + href + '"'), locale);
  }
});
bookingTest('failed network request is prevented from native navigation and remains retryable', async () => {
  const source = fs.readFileSync(path.join(root, 'dist/booking.js'), 'utf8');
  const inputs = Object.fromEntries(Object.entries({guest_name:'Example Guest',party_size:'2',arrival_date:'2027-01-31',arrival_time:'22:00',contact_email:'guest@example.test',note:'😀'.repeat(500),website:''}).map(([k,value])=>[k,{value}]));
  inputs.note.addEventListener=()=>{}; inputs.note.validity={customError:false}; inputs.note.setCustomValidity=msg=>{inputs.note.validity.customError=Boolean(msg)}; inputs.note.reportValidity=()=>false;
  inputs.translate_note = {checked:false, addEventListener:()=>{}};
  const noteCount={textContent:''};
  const form={elements:{namedItem: name=>inputs[name]}, reportValidity:()=>true, addEventListener:(_,fn)=>form.submit=fn};
  const button={disabled:true}, controls={disabled:true}, status={dataset:{},textContent:''};
  const messages={required:'required',sending:'sending',error:'network failed',noteTooLong:'too long'};
  const nodes={'#reservation-form':form,'#booking-messages':{textContent:JSON.stringify(messages)},'#submit-button':button,'#booking-controls':controls,'#form-status':status,'[data-note-count]':noteCount};
  const storage={getItem:()=>null,setItem:()=>{},removeItem:()=>{}};
  const document={body:{dataset:{locale:'en'}},querySelector:s=>nodes[s],querySelectorAll:()=>[]};
  let attempted=0, prevented=false;
  vm.runInNewContext(source,{document,Intl,Date,JSON,Object,Number,String,TextEncoder,crypto:webcrypto,sessionStorage:storage,fetch:async()=>{attempted++;throw Error('offline')}});
  assert.equal(controls.disabled,false); assert.equal(button.disabled,false);
  assert.equal(noteCount.textContent,'500');
  await form.submit({preventDefault:()=>{prevented=true}});
  assert.equal(prevented,true); assert.equal(attempted,1);
  assert.equal(status.dataset.kind,'error'); assert.equal(status.textContent,'network failed'); assert.equal(button.disabled,false);
  inputs.note.value='😀'.repeat(501); await form.submit({preventDefault:()=>{}});
  assert.equal(noteCount.textContent,'501'); assert.equal(status.textContent,'too long'); assert.equal(attempted,1);
});
bookingTest('initialization failure leaves all controls disabled', () => {
  const source=fs.readFileSync(path.join(root,'dist/booking.js'),'utf8');
  const controls={disabled:true}, button={disabled:true};
  const form={};
  const document={body:{dataset:{locale:'en'}},querySelector:s=>({'#reservation-form':form,'#booking-messages':{textContent:'invalid json'},'#booking-controls':controls,'#submit-button':button})[s]};
  assert.throws(()=>vm.runInNewContext(source,{document,JSON}));
  assert.equal(controls.disabled,true);
  assert.equal(button.disabled,true);
});
bookingTest('note translation follows disclosed page language without a picker', async () => {
  const source = fs.readFileSync(path.join(root, 'dist/booking.js'), 'utf8');
  for (const [locale, expected] of [['en','en'],['ja','ja'],['ko','en'],['th','en'],['zh-hans','en']]) {
    for (const consent of [false,true]) {
      const data={guest_name:'Example',party_size:'2',arrival_date:'2027-01-31',arrival_time:'22:00',contact_email:'example@example.test',note:'note',website:''};
      const inputs=Object.fromEntries(Object.entries(data).map(([key,value])=>[key,{value}]));
      inputs.note.addEventListener=()=>{};inputs.note.validity={customError:false};inputs.note.setCustomValidity=()=>{};
      inputs.translate_note={checked:consent,addEventListener:()=>{}};
      const form={elements:{namedItem:n=>inputs[n]},addEventListener:(name,fn)=>{if(name==='submit')form.submit=fn;},reportValidity:()=>true,reset:()=>{}};
      const nodes={'#reservation-form':form,'#booking-messages':{textContent:'{}'},'#submit-button':{},'#booking-controls':{},'#form-status':{dataset:{}},'[data-note-count]':{}};
      const document={body:{dataset:{locale}},querySelector:s=>nodes[s],querySelectorAll:()=>[]};
      let body;
      const fetch=async(url,options)=>{body=JSON.parse(options.body);return {ok:false}};
      vm.runInNewContext(source,{document,Intl,Date,JSON,Object,Number,String,TextEncoder,crypto:webcrypto,sessionStorage:{getItem:()=>null,setItem:()=>{}},fetch});
      await form.submit({preventDefault:()=>{}});
      assert.equal(body.locale,expected,locale); assert.equal(body.note_language,consent?expected:null,locale);
      assert.equal(body.translate_note,consent,locale);
    }
  }
});
