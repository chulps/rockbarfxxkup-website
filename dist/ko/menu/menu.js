(() => {
  const search = document.getElementById('menu-search');
  const category = document.getElementById('menu-category');
  const count = document.getElementById('menu-count');
  const clear = document.getElementById('menu-clear');
  const empty = document.getElementById('menu-empty');
  const requestForm = document.getElementById('menu-drink-request-form');
  const requestInput = document.getElementById('menu-drink-request');
  const requestConsent = document.getElementById('menu-drink-request-consent');
  const requestStatus = document.getElementById('menu-drink-request-status');
  const requestMessage = document.getElementById('menu-drink-request-message');
  const categoryControl = document.querySelector('.whisky-category-control');
  const groups = [...document.querySelectorAll('[data-menu-group]')];
  const rows = [...document.querySelectorAll('.menu-item')];
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase().trim();
  const countMeasureContext = document.createElement('canvas').getContext('2d');
  const track = (name, parameters = {}) => {
    if (typeof window.gtag !== 'function') return;
    window.gtag('event', name, {page_language: document.documentElement.lang, ...parameters});
  };

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
    return visible;
  }

  const knownTerms = new Map();
  groups.forEach(group => {
    const heading = group.querySelector('h2')?.textContent?.trim();
    if (heading) knownTerms.set(normalize(heading), heading);
    group.querySelectorAll('.menu-item-name').forEach(item => {
      const name = item.textContent.trim();
      if (name) knownTerms.set(normalize(name), name);
    });
  });
  let visibleResultCount = rows.length;
  let searchTimer;
  let searchFocusTracked = false;
  search.addEventListener('focus', () => {
    if (searchFocusTracked) return;
    searchFocusTracked = true;
    track('menu_search_focus');
  });
  search.addEventListener('input', () => {
    visibleResultCount = update();
    window.clearTimeout(searchTimer);
    if (!normalize(search.value)) return;
    searchTimer = window.setTimeout(() => {
      const parameters = {result_count: visibleResultCount};
      const knownTerm = knownTerms.get(normalize(search.value));
      if (visibleResultCount === 0) {
        track('menu_search_no_results', parameters);
      } else {
        if (knownTerm) parameters.search_term = knownTerm;
        track('menu_search', parameters);
      }
    }, 700);
  });
  category.addEventListener('change', () => {
    visibleResultCount = update();
    const selectedGroup = groups.find(group => group.dataset.categoryId === category.value);
    track('menu_category_select', {
      category_name: category.value === 'all' ? 'all' : selectedGroup?.querySelector('h2')?.textContent || 'unknown',
      result_count: visibleResultCount
    });
  });
  clear.addEventListener('click', () => {
    const hadActiveFilters = Boolean(normalize(search.value) || category.value !== 'all');
    search.value = '';
    category.value = 'all';
    visibleResultCount = update();
    track('menu_clear_filters', {had_active_filters: hadActiveFilters});
    search.focus();
  });

  if (requestForm && requestInput && requestConsent && requestStatus && requestMessage) {
    const messages = {
      en: {empty:'Tell us the drink name or style you were looking for.',consent:'Please confirm that you are submitting only a drink name or style.',length:'Please keep your request under 80 characters.',invalid:'Please use a drink name or style with letters, numbers, spaces, and common punctuation.',personal:'This may include personal information. Remove it and enter only a drink name or style.',suspicious:'Please enter only a drink name or style.',unavailable:'Your request could not be sent right now. Please try again later.',success:'Thanks. Your drink request was submitted. This is not confirmation that we currently serve it.'},
      ja: {empty:'お探しのドリンク名または種類を入力してください。',consent:'ドリンク名または種類のみを送信することを確認してください。',length:'80文字以内で入力してください。',invalid:'文字、数字、空白、一般的な句読点を使って入力してください。',personal:'個人情報が含まれている可能性があります。削除してドリンク名または種類のみ入力してください。',suspicious:'ドリンク名または種類のみ入力してください。',unavailable:'現在送信できません。しばらくしてからもう一度お試しください。',success:'リクエストを送信しました。ありがとうございます。現在提供していることを示すものではありません。'},
      ko: {empty:'찾으시는 음료 이름이나 종류를 입력해 주세요.',consent:'음료 이름이나 종류만 제출한다는 점을 확인해 주세요.',length:'요청은 80자 이내로 입력해 주세요.',invalid:'문자, 숫자, 공백, 일반적인 문장 부호를 사용해 주세요.',personal:'개인정보가 포함되었을 수 있습니다. 삭제하고 음료 이름이나 종류만 입력해 주세요.',suspicious:'음료 이름이나 종류만 입력해 주세요.',unavailable:'지금은 요청을 보낼 수 없습니다. 잠시 후 다시 시도해 주세요.',success:'음료 요청을 보냈습니다. 감사합니다. 현재 제공 중이라는 확인은 아닙니다.'},
      th: {empty:'โปรดระบุชื่อหรือประเภทเครื่องดื่มที่คุณกำลังมองหา',consent:'โปรดยืนยันว่าคุณส่งเฉพาะชื่อหรือประเภทเครื่องดื่ม',length:'โปรดระบุไม่เกิน 80 ตัวอักษร',invalid:'โปรดใช้ตัวอักษร ตัวเลข เว้นวรรค และเครื่องหมายวรรคตอนทั่วไป',personal:'ข้อความนี้อาจมีข้อมูลส่วนบุคคล โปรดลบออกและระบุเฉพาะชื่อหรือประเภทเครื่องดื่ม',suspicious:'โปรดระบุเฉพาะชื่อหรือประเภทเครื่องดื่ม',unavailable:'ขณะนี้ส่งคำขอไม่ได้ โปรดลองอีกครั้งภายหลัง',success:'ส่งคำขอเครื่องดื่มแล้ว ขอบคุณ นี่ไม่ได้ยืนยันว่ามีเครื่องดื่มนี้ให้บริการในขณะนี้'},
      'zh-Hans': {empty:'请填写您想找的饮品名称或类型。',consent:'请确认您只提交饮品名称或类型。',length:'请将内容控制在80个字符以内。',invalid:'请使用文字、数字、空格和常见标点。',personal:'内容可能包含个人信息。请删除后只填写饮品名称或类型。',suspicious:'请只填写饮品名称或类型。',unavailable:'现在无法提交，请稍后再试。',success:'饮品需求已提交，谢谢。这不代表我们目前提供该饮品。'}
    };
    const copy = messages[document.documentElement.lang] || messages.en;
    const collapse = value => value.normalize('NFKC').replace(/\s+/gu, ' ').trim();
    const validText = value => {
      let hasLetter = false;
      let digitCount = 0;
      const allowedPunctuation = " &.'’()-+,:!";
      for (const character of value) {
        const point = character.codePointAt(0);
        const latin = character.toLocaleLowerCase() !== character.toLocaleUpperCase();
        const unicodeLetter = latin || (point >= 0x3040 && point <= 0x30ff) || (point >= 0x3400 && point <= 0x9fff) || (point >= 0xac00 && point <= 0xd7af) || (point >= 0x0e00 && point <= 0x0e7f) || (point >= 0x20000 && point <= 0x2fa1f);
        const digit = point >= 0x30 && point <= 0x39;
        if (unicodeLetter) hasLetter = true;
        if (digit) digitCount += 1;
        if (!unicodeLetter && !digit && !allowedPunctuation.includes(character)) return false;
      }
      return hasLetter && digitCount < 7;
    };
    const personalInfo = value => /@|https?:|www\.|mailto:|\b(?:phone|mobile|email|address|my name|name is|call me|contact me|sapporo|hokkaido)\b|〒|丁目|番地|号|北海道|札幌市|中央区/i.test(value);
    const unsafeSyntax = value => {
      const forbidden = '<>`$;=\\{}[]|/"';
      if ([...value].some(character => forbidden.includes(character))) return true;
      return /--|\/\*|\*\/|\b(?:select|insert into|update|delete from|drop table|drop database|alter table|union select|exec|execute|pragma|truncate|grant|revoke|javascript|onerror|onload|alert\(|prompt\(|confirm\(|eval\(|fetch\(|document\.|window\.)/i.test(value);
    };
    const setStatus = (message, success = false) => {
      requestMessage.textContent = message;
      requestStatus.classList.toggle('is-error', Boolean(message) && !success);
      requestStatus.classList.toggle('is-success', Boolean(message) && success);
    };
    requestForm.addEventListener('submit', event => {
      event.preventDefault();
      const request = collapse(requestInput.value);
      setStatus('');
      if (!request) { setStatus(copy.empty); requestInput.focus(); return; }
      if (!requestConsent.checked) { setStatus(copy.consent); requestConsent.focus(); return; }
      if (request.length > 80) { setStatus(copy.length); requestInput.focus(); return; }
      if (!validText(request) || unsafeSyntax(request)) { setStatus(copy.invalid); requestInput.focus(); return; }
      if (personalInfo(request)) { setStatus(copy.personal); requestInput.focus(); return; }
      if (typeof window.gtag !== 'function') { setStatus(copy.unavailable); return; }
      track('menu_drink_request_submitted', {requested_drink: request, privacy_certified: true});
      requestInput.value = '';
      requestConsent.checked = false;
      setStatus(copy.success, true);
    });
  }
})();
