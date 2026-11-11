// Example-only simulation: weights match drawn wedges, not the bar's real odds.
(() => {
  const wheel = document.getElementById('whisky-wheel-svg');
  const spin = document.getElementById('whisky-wheel-spin');
  const result = document.getElementById('whisky-wheel-result');
  const status = document.getElementById('whisky-wheel-status');
  const message = document.getElementById('whisky-wheel-message');
  const prices = document.getElementById('whisky-wheel-prices');
  const data = document.getElementById('whisky-wheel-data');
  const details = document.querySelector('.whisky-wheel-demo');
  if (!wheel || !spin || !result || !status || !message || !prices || !data || !details) return;
  let config;
  try { config = JSON.parse(data.textContent); } catch { return; }
  const items = config.items;
  if (!Array.isArray(items) || !items.length || items.some(item => !item.name || !item.price || !Number.isFinite(item.weight) || item.weight <= 0)) return;
  const total = items.reduce((n, item) => n + item.weight, 0);
  const pages = {en:'https://www.rockbarfxxkup.com/whisky/',ja:'https://www.rockbarfxxkup.com/ja/whisky/',ko:'https://www.rockbarfxxkup.com/ko/whisky/',th:'https://www.rockbarfxxkup.com/th/whisky/','zh-Hans':'https://www.rockbarfxxkup.com/zh-hans/whisky/'};
  const allowedIds = new Set(['fuji_single_malt','tsunuki','hakushu_12','yoichi','hibiki_blenders_choice','yamazaki','miyagikyo','yamazaki_12','hakushu','taketsuru','nikka_from_the_barrel']);
  const locale = Object.hasOwn(pages, config.locale) ? config.locale : 'en';
  // Use the site's existing gtag and consent behavior. Never send input or raw URLs.
  const track = (eventName, itemId) => {
    try {
      if (typeof window.gtag !== 'function') return;
      const params = {page_language: locale, page_location: pages[locale], page_referrer: '', transport_type: 'beacon'};
      if (allowedIds.has(itemId)) params.example_result = itemId;
      window.gtag('event', eventName, params);
    } catch { /* Analytics must never interrupt the demo. */ }
  };
  details.addEventListener('toggle', () => { if (details.open) track('whisky_lottery_demo_open'); });
  let rotation = 0, busy = false;
  spin.disabled = false;
  spin.addEventListener('click', () => {
    if (busy) return;
    busy = true; spin.disabled = true;
    track('whisky_lottery_demo_spin');
    const draw = Math.random() * total;
    let cumulative = 0, index = items.length - 1, before = 0;
    for (let i = 0; i < items.length; i++) {
      before = cumulative; cumulative += items[i].weight;
      if (draw < cumulative) { index = i; break; }
    }
    const midpoint = (before + items[index].weight / 2) / total * 360;
    const desired = (360 - midpoint) % 360;
    const current = ((rotation % 360) + 360) % 360;
    rotation += 1800 + ((desired - current + 360) % 360);
    const reduced = typeof window.matchMedia === 'function' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    wheel.style.transition = reduced ? 'none' : 'transform 3.4s cubic-bezier(.12,.65,.16,1)';
    wheel.style.transform = 'rotate(' + rotation + 'deg)';
    status.textContent = config.spinning; result.textContent = config.spinning;
    message.textContent = ''; prices.textContent = '';
    window.setTimeout(() => {
      const item = items[index];
      status.textContent = config.example; result.textContent = item.name;
      message.textContent = config.nice;
      const comparison = item.saving
        ? `${config.savingLabel}: ${item.saving} (${config.savingBasis}).`
        : item.comparable ? config.noSaving : config.caveat;
      prices.textContent = `${config.menuLabel}: ${item.price}. ${config.lotteryLabel}: ${config.lotteryPrice}. ${comparison}`;
      track('whisky_lottery_demo_result', item.id);
      spin.textContent = config.again; spin.disabled = false; busy = false;
    }, reduced ? 0 : 3400);
  });
})();
