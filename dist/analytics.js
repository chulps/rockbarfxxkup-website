// Track actions without delaying or changing navigation. Completed tests are
// rollout versions, not ongoing experiment populations.
(() => {
  const experiment = window.firstVisitExperiment;
  const hero = document.querySelector('.hero-copy');
  const footer = document.getElementById('footer-contact');
  let viewed = false;
  let observer;
  function trackExposure() {
    if (viewed || !experiment?.copyApplied || typeof window.gtag !== 'function') return;
    viewed = true;
    window.gtag('event', 'experiment_view', {
      experiment_id: experiment.id,
      experiment_variant: experiment.variant,
      link_placement: 'hero',
      page_language: document.documentElement.lang,
      transport_type: 'beacon'
    });
    observer?.disconnect();
  }
  if (hero && experiment?.copyApplied && 'IntersectionObserver' in window) {
    observer = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.isIntersecting && entry.intersectionRatio >= 0.25)) trackExposure();
    }, {threshold: 0.25});
    observer.observe(hero);
  }
  document.addEventListener('click', event => {
    const link = event.target.closest('a[data-track-event]');
    if (!link || typeof window.gtag !== 'function') return;
    const eventName = link.dataset.trackEvent;
    const params = {
      page_language: document.documentElement.lang,
      link_placement: link.dataset.trackPlacement,
      link_url: link.href,
      transport_type: 'beacon'
    };
    if (link.dataset.trackDestination) params.link_destination = link.dataset.trackDestination;
    if (eventName === 'directions_click') {
      params.link_destination = 'google_maps';
      params.rollout_id = 'directions_button_test_2026_10';
      params.rollout_variant = 'B';
    } else if (eventName === 'menu_open') {
      params.link_destination = 'interactive_menu';
    } else if (eventName === 'phone_click') {
      params.link_destination = 'phone';
    }
    if (footer?.contains(link)) {
      params.link_placement = 'footer_contact';
      params.rollout_id = 'footer_contact_test_2026_10';
      params.rollout_variant = 'B';
    }
    // Seeing the hero or interacting with its CTA confirms exposure. Deep-link
    // visits that never see it are not counted as conversions in the next test.
    if (experiment?.copyApplied && hero?.contains(link)) trackExposure();
    if (experiment?.copyApplied && viewed) {
      params.experiment_id = experiment.id;
      params.experiment_variant = experiment.variant;
    }
    if (link.dataset.language) params.selected_language = link.dataset.language;
    window.gtag('event', eventName, params);
  }, {capture: true});
})();
