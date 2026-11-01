(() => {
  const search = document.getElementById('menu-search');
  const category = document.getElementById('menu-category');
  const count = document.getElementById('menu-count');
  const clear = document.getElementById('menu-clear');
  const empty = document.getElementById('menu-empty');
  const groups = [...document.querySelectorAll('[data-menu-group]')];
  const rows = [...document.querySelectorAll('.menu-item')];
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase().trim();

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
    count.textContent = `${visible} ${visible === 1 ? 'drink' : 'drinks'}`;
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
