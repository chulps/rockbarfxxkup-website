(() => {
  const controls = document.querySelector(".whisky-controls");
  if (!controls) return;

  const search = document.getElementById("whisky-search");
  const category = document.getElementById("whisky-category");
  const categoryControl = document.querySelector(".whisky-category-control");
  const clear = document.getElementById("whisky-clear");
  const count = document.getElementById("whisky-count");
  const empty = document.getElementById("whisky-empty");
  const suggestionForm = document.getElementById("whisky-suggestion-form");
  const suggestionInput = document.getElementById("whisky-suggestion");
  const suggestionCertify = document.getElementById("whisky-suggestion-certify");
  const suggestionStatus = document.getElementById("whisky-suggestion-status");
  const suggestionMessage = document.getElementById("whisky-suggestion-message");
  const groups = Array.from(document.querySelectorAll("[data-whisky-group]"));
  const japaneseNote = document.querySelector("[data-whisky-japanese-note]");
  if (!search || !category || !clear || !count || !empty) return;

  const track = (eventName, parameters = {}) => {
    if (typeof window.gtag !== "function") return;
    window.gtag("event", eventName, {
      page_language: document.documentElement.lang,
      ...parameters
    });
  };

  const countMeasureContext = document.createElement("canvas").getContext("2d");
  const positionCategoryCount = () => {
    if (!categoryControl || !countMeasureContext) return;
    const selectedLabel = category.options[category.selectedIndex]?.textContent || "";
    const style = window.getComputedStyle(category);
    countMeasureContext.font = style.font;
    const labelWidth = countMeasureContext.measureText(selectedLabel).width;
    const leftPadding = (Number.parseFloat(style.paddingLeft) || 13) + (Number.parseFloat(style.borderLeftWidth) || 0);
    const rightBorder = Number.parseFloat(style.borderRightWidth) || 0;
    const left = leftPadding + labelWidth + 8;
    const countWidth = count.getBoundingClientRect().width;
    if (left + countWidth <= category.clientWidth - 36) {
      count.style.left = left + "px";
      count.style.right = "auto";
      count.style.textAlign = "left";
      category.style.paddingRight = Math.ceil(category.clientWidth - rightBorder - left + 8) + "px";
    } else {
      count.style.left = "auto";
      count.style.right = "36px";
      count.style.textAlign = "right";
      category.style.paddingRight = Math.ceil(44 + countWidth) + "px";
    }
  };

  controls.hidden = false;
  positionCategoryCount();
  window.addEventListener("resize", positionCategoryCount);
  document.fonts?.ready.then(positionCategoryCount);

  const normalize = (value) => value.normalize("NFKC").toLocaleLowerCase().trim();
  const knownSearchTerms = new Map();
  groups.forEach((group) => {
    const categoryName = group.querySelector("h2")?.textContent?.trim();
    if (categoryName) knownSearchTerms.set(normalize(categoryName), categoryName);
    group.querySelectorAll(".whisky-name").forEach((item) => {
      const name = item.textContent.trim();
      if (name) knownSearchTerms.set(normalize(name), name);
    });
  });
  let visibleResultCount = document.querySelectorAll(".whisky-item").length;
  let searchTimer;
  let searchFocusTracked = false;
  const filterList = () => {
    const query = normalize(search.value);
    const selectedCategory = category.value;
    let visibleCount = 0;

    groups.forEach((group) => {
      const categoryMatches = selectedCategory === "all" || group.dataset.categoryId === selectedCategory;
      let groupCount = 0;
      group.querySelectorAll(".whisky-item").forEach((item) => {
        const matches = categoryMatches && (!query || normalize(item.dataset.search || item.textContent).includes(query));
        item.hidden = !matches;
        if (matches) {
          groupCount += 1;
          visibleCount += 1;
        }
      });
      group.hidden = groupCount === 0;
    });

    if (japaneseNote) {
      japaneseNote.hidden = !groups.some((group) => group.dataset.whiskyOrigin === "japanese" && !group.hidden);
    }

    const countSuffix = selectedCategory === "all" ? " " + count.dataset.suffix : "";
    count.textContent = "(" + visibleCount + countSuffix + ")";
    count.hidden = false;
    positionCategoryCount();
    empty.hidden = visibleCount !== 0;
    visibleResultCount = visibleCount;
    return visibleCount;
  };

  search.addEventListener("focus", () => {
    if (searchFocusTracked) return;
    searchFocusTracked = true;
    track("whisky_search_focus");
  });
  search.addEventListener("input", () => {
    filterList();
    window.clearTimeout(searchTimer);
    if (!normalize(search.value)) return;
    searchTimer = window.setTimeout(() => {
      const parameters = { result_count: visibleResultCount };
      const knownTerm = knownSearchTerms.get(normalize(search.value));
      if (visibleResultCount === 0) {
        track("whisky_search_no_results", parameters);
      } else {
        if (knownTerm) parameters.search_term = knownTerm;
        track("whisky_search", parameters);
      }
    }, 700);
  });
  category.addEventListener("change", () => {
    const resultCount = filterList();
    const selectedGroup = groups.find((group) => group.dataset.categoryId === category.value);
    track("whisky_category_select", {
      category_name: category.value === "all" ? "all" : selectedGroup?.querySelector("h2")?.textContent || "unknown",
      result_count: resultCount
    });
  });
  clear.addEventListener("click", () => {
    const hadActiveFilters = Boolean(normalize(search.value) || category.value !== "all");
    search.value = "";
    category.value = "all";
    filterList();
    track("whisky_clear_filters", { had_active_filters: hadActiveFilters });
    search.focus();
  });

  if (suggestionForm && suggestionInput && suggestionCertify && suggestionStatus && suggestionMessage) {
    const messages = {
      en: {empty:"Enter the whisky bottle name only.", consent:"Please confirm that you are submitting only a whisky bottle name.", length:"Please keep the bottle name under 80 characters.", invalid:"Please use only a bottle name with letters, numbers, spaces, and common punctuation.", personal:"This may include personal information. Remove it and enter only the whisky bottle name.", suspicious:"Ah-ah-ah. No code past the gate.", unavailable:"The suggestion could not be sent right now. Please try again later.", success:"Thanks. Your whisky suggestion was submitted."},
      ja: {empty:"ウイスキーの銘柄名を入力してください。", consent:"銘柄名のみを送信することを確認してください。", length:"銘柄名は80文字以内で入力してください。", invalid:"銘柄名には文字、数字、空白、一般的な句読点のみ使用できます。", personal:"個人情報が含まれている可能性があります。個人情報を削除し、銘柄名のみ入力してください。", suspicious:"あっ、あっ、あっ。コードはこのゲートの先に通せません。", unavailable:"現在送信できません。しばらくしてからもう一度お試しください。", success:"ウイスキーの候補を送信しました。ありがとうございます。"},
      ko: {empty:"위스키 제품명만 입력해 주세요.", consent:"위스키 제품명만 제출한다는 점을 확인해 주세요.", length:"제품명은 80자 이내로 입력해 주세요.", invalid:"제품명에는 문자, 숫자, 공백, 일반적인 문장 부호만 사용할 수 있습니다.", personal:"개인정보가 포함되었을 수 있습니다. 개인정보를 지우고 위스키 제품명만 입력해 주세요.", suspicious:"어어, 잠깐. 코드는 이 문을 통과할 수 없어요.", unavailable:"지금은 제출할 수 없습니다. 잠시 후 다시 시도해 주세요.", success:"위스키 제안을 보내 주셔서 감사합니다."},
      th: {empty:"โปรดกรอกเฉพาะชื่อวิสกี้", consent:"โปรดยืนยันว่าคุณส่งเฉพาะชื่อวิสกี้", length:"โปรดกรอกชื่อวิสกี้ไม่เกิน 80 ตัวอักษร", invalid:"ชื่อวิสกี้ใช้ได้เฉพาะตัวอักษร ตัวเลข เว้นวรรค และเครื่องหมายวรรคตอนทั่วไป", personal:"ข้อความนี้อาจมีข้อมูลส่วนบุคคล โปรดลบข้อมูลดังกล่าวและกรอกเฉพาะชื่อวิสกี้", suspicious:"เดี๋ยวก่อน! โค้ดผ่านประตูนี้ไปไม่ได้", unavailable:"ขณะนี้ส่งข้อมูลไม่ได้ โปรดลองอีกครั้งภายหลัง", success:"ส่งชื่อวิสกี้ที่แนะนำแล้ว ขอบคุณ"},
      "zh-Hans": {empty:"请只填写威士忌酒款名称。", consent:"请确认您只提交威士忌酒款名称。", length:"酒款名称请控制在80个字符以内。", invalid:"酒款名称只能包含文字、数字、空格和常见标点。", personal:"内容可能包含个人信息。请删除个人信息，只填写威士忌酒款名称。", suspicious:"哎哎哎，代码不能通过这道门。", unavailable:"现在无法提交，请稍后再试。", success:"威士忌酒款建议已提交，谢谢。"}
    };
    const copy = messages[document.documentElement.lang] || messages.en;
    const collapseWhitespace = (value) => {
      let result = "";
      let pendingSpace = false;
      for (const character of value.normalize("NFKC")) {
        if (character.trim() === "") {
          if (result) pendingSpace = true;
          continue;
        }
        if (pendingSpace) result += " ";
        result += character;
        pendingSpace = false;
      }
      return result.trim();
    };
    const hasOnlyBottleNameCharacters = (value) => {
      let hasLetter = false;
      let digitCount = 0;
      const allowedPunctuation = " &.'’()-";
      for (const character of value) {
        const point = character.codePointAt(0);
        const isLatinLetter = character.toLocaleLowerCase() !== character.toLocaleUpperCase();
        const isCjkLetter = (point >= 0x3040 && point <= 0x30ff) ||
          (point >= 0x3400 && point <= 0x9fff) ||
          (point >= 0xac00 && point <= 0xd7af) ||
          (point >= 0x0e00 && point <= 0x0e7f) ||
          (point >= 0x20000 && point <= 0x2fa1f);
        const isDigit = point >= 0x30 && point <= 0x39;
        if (isLatinLetter || isCjkLetter) hasLetter = true;
        if (isDigit) digitCount += 1;
        if (!isLatinLetter && !isCjkLetter && !isDigit && !allowedPunctuation.includes(character)) return false;
      }
      return hasLetter && digitCount < 7;
    };
    const containsPersonalInfoClue = (value) => {
      const lower = value.toLocaleLowerCase();
      const clues = [
        "@", "http", "www.", "mailto:", "street", "road", "avenue", "address", "apartment",
        "phone", "mobile", "email", "my name", "name is", "call me", "contact me", "hokkaido",
        "sapporo", "chuo-ku", "chome", "banchi", "〒", "丁目", "番地", "号", "北海道", "札幌市", "中央区"
      ];
      return clues.some((clue) => lower.includes(clue));
    };
    const containsCodeOrQuerySyntax = (value) => {
      const forbiddenCharacters = "<>`$;=\\{}[]|/\\\"";
      for (const character of value) {
        if (forbiddenCharacters.includes(character)) return true;
      }
      const lower = value.toLocaleLowerCase();
      const suspiciousText = [
        "--", "/*", "*/", "select ", "insert into", "update ", "delete from", "drop table",
        "drop database", "alter table", "union select", "exec ", "execute ", "pragma ",
        "truncate ", "grant ", "revoke ", "javascript", "<script", "onerror", "onload",
        "alert(", "prompt(", "confirm(", "eval(", "fetch(", "document.", "window."
      ];
      return suspiciousText.some((token) => lower.includes(token));
    };
    const setSuggestionStatus = (message, kind = "error") => {
      suggestionMessage.textContent = message;
      suggestionStatus.classList.toggle("is-error", kind === "error" && Boolean(message));
      suggestionStatus.classList.toggle("is-success", kind === "success" && Boolean(message));
    };

    suggestionForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const suggestion = collapseWhitespace(suggestionInput.value);
      setSuggestionStatus("");

      if (!suggestion) {
        setSuggestionStatus(copy.empty);
        suggestionInput.focus();
        return;
      }
      if (!suggestionCertify.checked) {
        setSuggestionStatus(copy.consent);
        suggestionCertify.focus();
        return;
      }
      if (suggestion.length > 80) {
        setSuggestionStatus(copy.length);
        suggestionInput.focus();
        return;
      }
      if (!hasOnlyBottleNameCharacters(suggestion)) {
        setSuggestionStatus(copy.suspicious);
        suggestionInput.focus();
        return;
      }
      if (containsPersonalInfoClue(suggestion)) {
        setSuggestionStatus(copy.personal);
        suggestionInput.focus();
        return;
      }
      if (containsCodeOrQuerySyntax(suggestion)) {
        setSuggestionStatus(copy.suspicious);
        suggestionInput.focus();
        return;
      }
      if (typeof window.gtag !== "function") {
        setSuggestionStatus(copy.unavailable);
        return;
      }

      track("whisky_suggestion_submitted", {
        suggested_whisky_name: suggestion,
        privacy_certified: true
      });
      suggestionInput.value = "";
      suggestionCertify.checked = false;
      setSuggestionStatus(copy.success, "success");
    });
  }
})();
