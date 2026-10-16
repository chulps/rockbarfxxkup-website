// Track explicit visitor actions without changing link navigation.
(() => {
  const experiment = window.siteExperiment;
  const experimentParams = experiment ? {
    experiment_id: experiment.id,
    experiment_variant: experiment.variant
  } : {};

  // This is the exposure denominator for the persistent A/B assignment.
  if (experiment && typeof window.gtag === 'function') {
    window.gtag('event', 'experiment_view', {
      ...experimentParams,
      page_language: document.documentElement.lang,
      transport_type: 'beacon'
    });
  }

  document.addEventListener('click', event => {
    const link = event.target.closest('a[data-track-event]');
    if (!link || typeof window.gtag !== 'function') return;
    const params = {
      page_language: document.documentElement.lang,
      link_placement: link.dataset.trackPlacement,
      ...experimentParams,
      transport_type: 'beacon'
    };
    if (link.dataset.language) params.selected_language = link.dataset.language;
    window.gtag('event', link.dataset.trackEvent, params);
  }, {capture: true});
})();
