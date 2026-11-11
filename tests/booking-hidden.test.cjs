const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const read = p => fs.readFileSync(path.join(root, p), 'utf8');

test('all five booking URLs are unavailable and do not contain a request form', () => {
  for (const lang of ['', 'ja/', 'ko/', 'th/', 'zh-hans/']) {
    const html=read('dist/'+lang+'book/index.html');
    assert.match(html, /noindex/); assert.doesNotMatch(html, /<form\b|booking\.js|reservations\/requests/i);
    assert.ok(html.includes('href="/'+lang+'"'), lang);
  }
});
test('no homepage links to booking and sitemap excludes it', () => {
  for (const lang of ['', 'ja/', 'ko/', 'th/', 'zh-hans/']) {
    const html=read('dist/'+lang+'index.html');
    assert.doesNotMatch(html, /href="\/(?:ja\/|ko\/|th\/|zh-hans\/)?book\//);
    assert.doesNotMatch(html, /data-track-event="booking_open"/);
  }
  assert.doesNotMatch(read('dist/sitemap.xml'), /\/book\//);
});
test('published script cannot submit requests, while original source remains recoverable', () => {
  assert.doesNotMatch(read('dist/booking.js'), /fetch\s*\(|reservations\/requests/);
  assert.match(read('dist/booking.js'), /preventDefault/);
  assert.match(read('source/booking.js'), /reservations\/requests/);
  assert.match(read('source/booking.html'), /id="reservation-form"/);
});
