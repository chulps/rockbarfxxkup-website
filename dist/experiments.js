// The next test is prepared, but a strict false-by-default configuration gates
// assignment, copy changes and analytics. URL parameters cannot launch it.
(() => {
  const config = window.FXXKUP_EXPERIMENT_CONFIG?.firstVisit;
  if (!config || config.enabled !== true) return;
  const language = document.documentElement.lang;
  const copy = config.copy[language];
  if (!copy) return;
  let variant;
  try {
    variant = localStorage.getItem(config.storageKey);
    if (variant !== 'A' && variant !== 'B') {
      variant = Math.random() < config.allocation ? 'A' : 'B';
      localStorage.setItem(config.storageKey, variant);
      if (localStorage.getItem(config.storageKey) !== variant) return;
    }
  } catch {
    // A visitor without persistent storage sees the existing copy and is not
    // enrolled, rather than switching arms on every page or language change.
    return;
  }
  const experiment = {id: config.id, variant, copyApplied: false};
  window.firstVisitExperiment = experiment;
  window.fxxkupFirstVisit = {
    applyCopy() {
      if (experiment.copyApplied) return;
      const headline = document.querySelector('.hero-line');
      const supporting = document.querySelector('.hero-desc');
      if (!headline || !supporting) return;
      if (variant === 'B') {
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
