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

  const footerExperiment = window.footerExperiment;
  const footer = document.getElementById('footer-contact');
  let footerViewed = false;
  function trackFooterView() {
    if (footerViewed || !footerExperiment || typeof window.gtag !== 'function') return;
    footerViewed = true;
    window.gtag('event', 'experiment_view', {
      experiment_id: footerExperiment.id,
      experiment_variant: footerExperiment.variant,
      link_placement: 'footer_contact',
      page_language: document.documentElement.lang,
      transport_type: 'beacon'
    });
  }
  if (footer && footerExperiment && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.isIntersecting)) {
        trackFooterView();
        observer.disconnect();
      }
    }, {threshold: 0.25});
    observer.observe(footer);
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
    if (link.dataset.trackDestination) {
      params.link_destination = link.dataset.trackDestination;
      params.link_url = link.href;
    }
    if (footer && footer.contains(link) && footerExperiment) {
      // Click also confirms exposure if the observer has not run yet.
      trackFooterView();
      params.experiment_id = footerExperiment.id;
      params.experiment_variant = footerExperiment.variant;
      params.link_placement = 'footer_contact';
    }
    if (link.dataset.language) params.selected_language = link.dataset.language;
    window.gtag('event', link.dataset.trackEvent, params);
  }, {capture: true});
})();
