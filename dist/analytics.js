// Track explicit visitor actions without changing link navigation.
(() => {
  document.addEventListener('click', event => {
    const link = event.target.closest('a[data-track-event]');
    if (!link || typeof window.gtag !== 'function') return;
    const params = {
      page_language: document.documentElement.lang,
      link_placement: link.dataset.trackPlacement,
      transport_type: 'beacon'
    };
    if (link.dataset.language) params.selected_language = link.dataset.language;
    window.gtag('event', link.dataset.trackEvent, params);
  }, {capture: true});
})();
