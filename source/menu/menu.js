(() => {
  const search = document.getElementById('menu-search');
  const category = document.getElementById('menu-category');
  const count = document.getElementById('menu-count');
  const clear = document.getElementById('menu-clear');
  const empty = document.getElementById('menu-empty');
  const categoryControl = document.querySelector('.whisky-category-control');
  const groups = [...document.querySelectorAll('[data-menu-group]')];
  const rows = [...document.querySelectorAll('.menu-item')];
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase().trim();
  const countMeasureContext = document.createElement('canvas').getContext('2d');

  function positionCategoryCount() {
    if (!categoryControl || !countMeasureContext) return;
    const selectedLabel = category.options[category.selectedIndex]?.textContent || '';
    const style = window.getComputedStyle(category);
    countMeasureContext.font = style.font;
    const labelWidth = countMeasureContext.measureText(selectedLabel).width;
    const leftPadding = (Number.parseFloat(style.paddingLeft) || 13) + (Number.parseFloat(style.borderLeftWidth) || 0);
    const rightBorder = Number.parseFloat(style.borderRightWidth) || 0;
    const left = leftPadding + labelWidth + 8;
    const countWidth = count.getBoundingClientRect().width;
    if (left + countWidth <= category.clientWidth - 36) {
      count.style.left = left + 'px';
      count.style.right = 'auto';
      count.style.textAlign = 'left';
      category.style.paddingRight = Math.ceil(category.clientWidth - rightBorder - left + 8) + 'px';
    } else {
      count.style.left = 'auto';
      count.style.right = '36px';
      count.style.textAlign = 'right';
      category.style.paddingRight = Math.ceil(44 + countWidth) + 'px';
    }
  }

  positionCategoryCount();
  window.addEventListener('resize', positionCategoryCount);
  document.fonts?.ready.then(positionCategoryCount);

  function update() {
    const query = normalize(search.value);
    const selected = category.value;
    let visible = 0;
    groups.forEach(group => {
      const categoryMatches = selected === 'all' || group.dataset.categoryId === selected;
      let groupVisible = 0;
      group.querySelectorAll('.menu-item').forEach(row => {
        const matches = categoryMatches && (!query || normalize(row.dataset.search).includes(query));
        row.hidden = !matches;
        if (matches) groupVisible += 1;
      });
      group.hidden = groupVisible === 0;
      visible += groupVisible;
    });
    const unit = visible === 1 ? count.dataset.unitSingular : count.dataset.unitPlural;
    const separator = count.dataset.unitSpace === 'false' ? '' : ' ';
    count.textContent = `(${visible}${separator}${unit})`;
    positionCategoryCount();
    empty.hidden = visible !== 0;
  }

  search.addEventListener('input', update);
  category.addEventListener('change', update);
  clear.addEventListener('click', () => {
    search.value = '';
    category.value = 'all';
    update();
    search.focus();
  });
})();
