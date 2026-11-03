const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { webcrypto } = require('node:crypto');
const { TextEncoder } = require('node:util');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
test('localized pages keep fields and submit disabled without initialization', () => {
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
test('failed network request is prevented from native navigation and remains retryable', async () => {
  const source = fs.readFileSync(path.join(root, 'dist/booking.js'), 'utf8');
  const inputs = Object.fromEntries(Object.entries({guest_name:'Example Guest',party_size:'2',arrival_date:'2027-01-31',arrival_time:'22:00',contact_email:'guest@example.test',note:'hello',website:''}).map(([k,value])=>[k,{value}]));
  const form={elements:{namedItem: name=>inputs[name]}, reportValidity:()=>true, addEventListener:(_,fn)=>form.submit=fn};
  const button={disabled:true}, controls={disabled:true}, status={dataset:{},textContent:''};
  const messages={required:'required',sending:'sending',error:'network failed'};
  const nodes={'#reservation-form':form,'#booking-messages':{textContent:JSON.stringify(messages)},'#submit-button':button,'#booking-controls':controls,'#form-status':status};
  const storage={getItem:()=>null,setItem:()=>{},removeItem:()=>{}};
  const document={body:{dataset:{locale:'en'}},querySelector:s=>nodes[s],querySelectorAll:()=>[]};
  let attempted=0, prevented=false;
  vm.runInNewContext(source,{document,Intl,Date,JSON,Object,Number,String,TextEncoder,crypto:webcrypto,sessionStorage:storage,fetch:async()=>{attempted++;throw Error('offline')}});
  assert.equal(controls.disabled,false); assert.equal(button.disabled,false);
  await form.submit({preventDefault:()=>{prevented=true}});
  assert.equal(prevented,true); assert.equal(attempted,1);
  assert.equal(status.dataset.kind,'error'); assert.equal(status.textContent,'network failed'); assert.equal(button.disabled,false);
});
test('initialization failure leaves all controls disabled', () => {
  const source=fs.readFileSync(path.join(root,'dist/booking.js'),'utf8');
  const controls={disabled:true}, button={disabled:true};
  const form={};
  const document={body:{dataset:{locale:'en'}},querySelector:s=>({'#reservation-form':form,'#booking-messages':{textContent:'invalid json'},'#booking-controls':controls,'#submit-button':button})[s]};
  assert.throws(()=>vm.runInNewContext(source,{document,JSON}));
  assert.equal(controls.disabled,true);
  assert.equal(button.disabled,true);
});
