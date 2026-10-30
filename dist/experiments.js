// Fixed-horizon tests; completed rollouts never emit experiment exposures.
(() => {
  const config = window.FXXKUP_EXPERIMENT_CONFIG?.firstVisit;
  if (!config) return;
  const language = document.documentElement.lang;
  const now = Date.now();
  const started = !config.startsAt || now >= Date.parse(config.startsAt);
  const ended = config.endsAt && now >= Date.parse(config.endsAt);
  const expired = config.endsAt && now >= Date.parse(config.endsAt) + 86400000;
  let running = config.enabled === true && started && !expired;
  const fallback = config.rolloutVariant || 'A';
  let variant;
  if (!running) variant = fallback;
  else try {
    variant = localStorage.getItem(config.storageKey);
    if (variant !== 'A' && variant !== 'B') {
      if (ended) { running = false; variant = fallback; }
      else {
        variant = Math.random() < config.allocation ? 'A' : 'B';
        localStorage.setItem(config.storageKey, variant);
        if (localStorage.getItem(config.storageKey) !== variant) return;
      }
    }
  } catch {
    // Storage-blocked visitors get the current incumbent, without enrollment.
    running = false;
    variant = fallback;
  }
  const copy = variant === 'B' ? config.copy?.[language] : config.controlCopy?.[language];
  if (running && !config.copy?.[language]) return;
  const experiment = {id: config.id, variant, copyApplied: false};
  if (running) window.firstVisitExperiment = experiment;
  window.fxxkupFirstVisit = {
    applyCopy() {
      if (experiment.copyApplied) return;
      const headline = document.querySelector('.hero-line');
      const supporting = document.querySelector('.hero-desc');
      if (!headline || !supporting) return;
      if (copy) {
        const nodes = [];
        copy.lines.forEach((line, i) => {
          if (i) nodes.push(document.createElement('br'));
          nodes.push(document.createTextNode((i ? ' ' : '') + line));
        });
        headline.replaceChildren(...nodes);
        supporting.textContent = copy.supporting;
      }
      experiment.copyApplied = true;
    }
  };
})();
