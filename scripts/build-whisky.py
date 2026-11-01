from html import escape
from pathlib import Path
import json
import re
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "whisky"
DIST = ROOT / "dist"
ORIGIN = "https://www.rockbarfxxkup.com"

LANGUAGES = [
    {"code": "en", "folder": "", "file": "whisky-inventory.md", "title_prefix": "Page title: ", "description_prefix": "Page description: "},
    {"code": "ja", "folder": "ja", "file": "whisky-inventory-ja.md", "title_prefix": "ページタイトル案：", "description_prefix": "ページ紹介文案："},
    {"code": "ko", "folder": "ko", "file": "whisky-inventory-ko.md", "title_prefix": "페이지 제목 제안: ", "description_prefix": "페이지 소개 문구 제안: "},
    {"code": "th", "folder": "th", "file": "whisky-inventory-th.md", "title_prefix": "ชื่อหน้าแนะนำ: ", "description_prefix": "ข้อความแนะนำหน้า: "},
    {"code": "zh-Hans", "folder": "zh-hans", "file": "whisky-inventory-zh-hans.md", "title_prefix": "页面标题建议：", "description_prefix": "页面简介建议："},
]
ACTIVE_LANGUAGES = LANGUAGES

LABELS = {
    "en": {"home": "Home", "drinks": "Drinks", "find": "Find us", "language": "Language", "languages": "Website language", "search": "Search whiskies", "placeholder": "Search bottle names or styles", "category": "Category", "all": "All categories", "all_count": "All categories", "clear": "Clear", "count": "whiskies", "no_results": "No whiskies match that search.", "notes": "Menu notes", "area": "WHISKY / MENU", "privacy": "Privacy policy", "directions": "Get directions", "instagram": "Instagram", "full_menu": "Full drinks menu", "availability": "Selection and availability can change."},
    "ja": {"home": "ホーム", "drinks": "ドリンク", "find": "アクセス", "language": "言語", "languages": "ウェブサイトの言語", "search": "ウイスキーを検索", "placeholder": "銘柄やタイプで検索", "category": "カテゴリー", "all": "すべてのカテゴリー", "all_count": "すべてのカテゴリー（{count}銘柄）", "clear": "クリア", "count": "銘柄", "no_results": "該当するウイスキーがありません。", "notes": "メニュー情報の確認事項", "area": "ウイスキー / メニュー", "privacy": "プライバシーポリシー", "directions": "アクセス", "instagram": "Instagram", "full_menu": "ドリンク全メニュー", "availability": "銘柄と在庫状況は変更されることがあります。"},
    "ko": {"home": "홈", "drinks": "음료", "find": "오시는 길", "language": "언어", "languages": "웹사이트 언어", "search": "위스키 검색", "placeholder": "이름이나 종류로 검색", "category": "분류", "all": "전체 분류", "all_count": "전체 분류 ({count}종)", "clear": "지우기", "count": "종", "no_results": "검색 결과가 없습니다.", "notes": "메뉴 데이터 확인 사항", "area": "위스키 / 메뉴", "privacy": "개인정보 처리방침", "directions": "오시는 길", "instagram": "Instagram", "full_menu": "전체 음료 메뉴", "availability": "메뉴 구성과 재고는 변경될 수 있습니다."},
    "th": {"home": "หน้าแรก", "drinks": "เครื่องดื่ม", "find": "เส้นทาง", "language": "ภาษา", "languages": "ภาษาเว็บไซต์", "search": "ค้นหาวิสกี้", "placeholder": "ค้นหาตามชื่อหรือประเภท", "category": "หมวดหมู่", "all": "ทุกหมวดหมู่", "all_count": "ทุกหมวดหมู่ ({count} รายการ)", "clear": "ล้าง", "count": "รายการ", "no_results": "ไม่พบวิสกี้ที่ตรงกับการค้นหา", "notes": "หมายเหตุเกี่ยวกับข้อมูลเมนู", "area": "วิสกี้ / เมนู", "privacy": "นโยบายความเป็นส่วนตัว", "directions": "เส้นทาง", "instagram": "Instagram", "full_menu": "เมนูเครื่องดื่มทั้งหมด", "availability": "รายการและสินค้าที่มีจำหน่ายอาจเปลี่ยนแปลงได้"},
    "zh-Hans": {"home": "首页", "drinks": "饮品", "find": "到店路线", "language": "语言", "languages": "网站语言", "search": "搜索威士忌", "placeholder": "按酒款或类型搜索", "category": "分类", "all": "所有分类", "all_count": "所有分类（{count}款）", "clear": "清除", "count": "款", "no_results": "没有找到匹配的威士忌。", "notes": "菜单数据备注", "area": "威士忌 / 酒单", "privacy": "隐私政策", "directions": "到店路线", "instagram": "Instagram", "full_menu": "完整饮品菜单", "availability": "酒款与库存情况可能会有变化。"},
}

FORM_COPY = {
    "en": {"empty_copy": "Sorry, that whisky isn’t on our list. Please let us know which bottle you were looking for.", "suggestion_label": "Whisky bottle name", "suggestion_note": "Submitting sends the bottle name to Google Analytics so we can understand what visitors are looking for. Enter the bottle name only; do not include your name, address, phone number, email address, or other personal information.", "certify": "I certify that this is only a whisky bottle name and contains no personal information.", "submit": "Submit", "map_label": "Google Maps location guide", "map_title": "Google Maps area guide for Rock Bar FxxK Up in Susukino, Sapporo"},
    "ja": {"empty_copy": "お探しのウイスキーはメニューにありません。ご希望の銘柄をお知らせください。", "suggestion_label": "ウイスキーの銘柄名", "suggestion_note": "送信すると、どの銘柄が探されているかを知るために、ボトル名がGoogle アナリティクスに送信されます。銘柄名のみを入力し、氏名、住所、電話番号、メールアドレスなどの個人情報は入力しないでください。", "certify": "入力内容がウイスキーの銘柄名のみで、個人情報を含まないことを確認します。", "submit": "送信", "map_label": "Google マップで周辺を見る", "map_title": "札幌・すすきののRock Bar FxxK Up周辺マップ"},
    "ko": {"empty_copy": "찾으시는 위스키가 메뉴에 없습니다. 원하셨던 제품명을 알려주세요.", "suggestion_label": "위스키 제품명", "suggestion_note": "제출하면 방문자가 어떤 제품을 찾는지 파악하기 위해 제품명이 Google 애널리틱스로 전송됩니다. 제품명만 입력하고 이름, 주소, 전화번호, 이메일 주소 등 개인정보는 입력하지 마세요.", "certify": "입력 내용이 위스키 제품명만 포함하며 개인정보가 없음을 확인합니다.", "submit": "제출", "map_label": "Google 지도 위치 안내", "map_title": "삿포로 스스키노 Rock Bar FxxK Up 주변 지도"},
    "th": {"empty_copy": "ไม่มีวิสกี้ที่ค้นหาในรายการของเรา โปรดแจ้งชื่อขวดที่คุณกำลังมองหา", "suggestion_label": "ชื่อวิสกี้", "suggestion_note": "เมื่อส่ง ชื่อวิสกี้จะถูกส่งไปยัง Google Analytics เพื่อให้เราเข้าใจว่าผู้เข้าชมกำลังมองหาอะไร โปรดกรอกเฉพาะชื่อวิสกี้ และอย่าระบุชื่อ ที่อยู่ หมายเลขโทรศัพท์ อีเมล หรือข้อมูลส่วนบุคคลอื่น ๆ", "certify": "ขอยืนยันว่าข้อความนี้มีเพียงชื่อวิสกี้และไม่มีข้อมูลส่วนบุคคล", "submit": "ส่ง", "map_label": "แผนที่ตำแหน่ง Google Maps", "map_title": "แผนที่บริเวณ Rock Bar FxxK Up ในซูซูกิโนะ ซัปโปโร"},
    "zh-Hans": {"empty_copy": "我们暂时没有这款威士忌。请告诉我们您想找的酒款名称。", "suggestion_label": "威士忌酒款名称", "suggestion_note": "提交后，酒款名称会发送至 Google Analytics，帮助我们了解访客正在寻找哪些酒款。请只填写酒款名称，不要填写姓名、地址、电话号码、电子邮箱或其他个人信息。", "certify": "我确认这里只填写威士忌酒款名称，不含个人信息。", "submit": "提交", "map_label": "Google 地图位置指南", "map_title": "札幌薄野 Rock Bar FxxK Up 周边地图"},
}

TITLE_FALLBACK = "Sapporo Whiskey Bar Menu & Prices | Rock Bar FxxK Up"
DESCRIPTION_FALLBACK = "Browse Japanese whisky, Scotch, bourbon and more at Rock Bar FxxK Up, a whisky bar in Susukino, Sapporo. Check menu prices and directions before you visit."
NOTE_HEADINGS = {
    "en": "Menu data notes",
    "ja": "メニュー情報の確認事項",
    "ko": "메뉴 데이터 확인 사항",
    "th": "หมายเหตุเกี่ยวกับข้อมูลเมนู",
    "zh-Hans": "菜单数据备注",
}

def parse_inventory(config):
    text = (SOURCE / config["file"]).read_text(encoding="utf-8")
    heading = ""
    page_title = TITLE_FALLBACK
    description = DESCRIPTION_FALLBACK
    source_line = ""
    groups = []
    notes = []
    in_notes = False

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("# ") and not heading:
            heading = line[2:].strip()
            continue
        if line.startswith(config["title_prefix"]):
            page_title = line[len(config["title_prefix"]):].strip()
            continue
        if line.startswith(config["description_prefix"]):
            description = line[len(config["description_prefix"]):].strip()
            continue
        if not source_line and (line.startswith("Source:") or line.startswith("出典：") or line.startswith("最終更新日：") or line.startswith("출처:") or line.startswith("최종 업데이트:") or line.startswith("ที่มา:") or line.startswith("อัปเดตล่าสุด:") or line.startswith("来源：") or line.startswith("最后更新：") or line.startswith("Last updated ")):
            source_line = line
            continue
        if line.startswith("## "):
            category_name = line[3:].strip()
            if category_name == NOTE_HEADINGS[config["code"]]:
                in_notes = True
            else:
                groups.append({"name": category_name, "items": []})
                in_notes = False
            continue
        if line.startswith("- "):
            entry = line[2:].strip()
            if in_notes:
                notes.append(entry)
            elif groups:
                name, sep, price = entry.partition(" — ")
                groups[-1]["items"].append({"name": name.strip(), "price": price.strip() if sep else ""})
            continue
        if in_notes:
            notes.append(line)

    if not heading or not groups:
        raise ValueError("Inventory source is missing its heading or categories: " + config["file"])
    return {"heading": heading, "title": page_title, "description": description, "source": source_line, "groups": groups, "notes": notes}

def locale_root(config):
    return "/" if not config["folder"] else "/" + config["folder"] + "/"

def page_url(config):
    return ORIGIN + locale_root(config) + "whisky/"

def render_page(config, inventory, menu_urls):
    code = config["code"]
    label = LABELS[code]
    form_copy = FORM_COPY[code]
    lang_root = locale_root(config)
    canonical = page_url(config)
    hreflang_links = "\n".join(
        '<link rel="alternate" hreflang="' + escape(other["code"], quote=True) + '" href="' + escape(page_url(other), quote=True) + '">'
        for other in ACTIVE_LANGUAGES
    ) + '\n<link rel="alternate" hreflang="x-default" href="' + escape(page_url(ACTIVE_LANGUAGES[0]), quote=True) + '">'
    language_options = "\n".join(
        '<a href="' + escape(menu_urls[other["code"]], quote=True) + '" hreflang="' + escape(other["code"], quote=True) + '" lang="' + escape(other["code"], quote=True) + '" data-language="' + escape(other["code"], quote=True) + '" data-track-event="whisky_language_select" data-track-placement="language_menu"' + (' aria-current="page"' if other["code"] == code else '') + '>' + {"en": "English", "ja": "日本語", "ko": "한국어", "th": "ไทย", "zh-Hans": "简体中文"}[other["code"]] + '</a>'
        for other in LANGUAGES
    )
    category_options = ['<option value="all">' + escape(label["all"]) + '</option>']
    category_sections = []
    flat_names = []
    for index, group in enumerate(inventory["groups"], 1):
        category_id = str(index)
        category_options.append('<option value="' + category_id + '">' + escape(group["name"]) + '</option>')
        items_html = []
        for item in group["items"]:
            name = item["name"]
            price = item["price"]
            flat_names.append(name)
            search_value = escape(name + " " + price + " " + group["name"], quote=True)
            price = price.replace("15ml", {"en":"15ml", "ja":"15ml", "ko":"15ml", "th":"15 มล.", "zh-Hans":"15毫升"}[code]).replace("30ml", {"en":"30ml", "ja":"30ml", "ko":"30ml", "th":"30 มล.", "zh-Hans":"30毫升"}[code])
            note_match = re.match(r"^(.*?)(?:\s+([（(].*[）)]))$", price)
            if note_match:
                price_html = '<span class="whisky-price-value">' + escape(note_match.group(1).strip()) + '</span><span class="whisky-item-note">' + escape(note_match.group(2).strip()) + '</span>'
            else:
                price_html = '<span class="whisky-price-value">' + escape(price) + '</span>'
            items_html.append('<li class="whisky-item" data-search="' + search_value + '"><span class="whisky-name">' + escape(name) + '</span><span class="whisky-price">' + price_html + '</span></li>')
        category_sections.append('<section class="whisky-category" data-whisky-group data-category-id="' + category_id + '"><h2 id="category-' + category_id + '">' + escape(group["name"]) + '</h2><ul class="whisky-list">' + "".join(items_html) + '</ul></section>')

    initial_count = sum(len(group["items"]) for group in inventory["groups"])
    category_options[0] = '<option value="all">' + escape(label["all"]) + '</option>'
    source_note = '<p class="whisky-updated">' + escape(inventory["source"]) + '</p>' if inventory["source"] else ""
    privacy_href = "/privacy/#ja" if code == "ja" else "/privacy/#en"
    website_schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": inventory["title"],
        "description": inventory["description"],
        "url": canonical,
        "inLanguage": code,
        "isPartOf": {"@type": "WebSite", "name": "Rock Bar FxxK Up", "url": ORIGIN + "/"},
        "about": {"@type": "BarOrPub", "name": "Rock Bar FxxK Up", "url": ORIGIN + "/"},
        "mainEntity": {"@type": "ItemList", "numberOfItems": initial_count, "itemListElement": [{"@type": "ListItem", "position": pos, "name": name} for pos, name in enumerate(flat_names, 1)]},
    }
    description = escape(inventory["description"], quote=True)
    title = escape(inventory["title"])
    schema = json.dumps(website_schema, ensure_ascii=False).replace("</", "<\\/")
    external_icon = '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19 19 5M5 5h14v14"></path></svg>'
    body = f'''<!doctype html>
<html lang="{escape(code, quote=True)}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#161414">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{escape(canonical, quote=True)}">
{hreflang_links}
<link rel="icon" href="/assets/logo.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800;900&amp;family=DM+Sans:wght@400;500;600;700&amp;family=Noto+Sans+JP:wght@400;600;800&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
<script src="/whisky.js" defer></script>
<script>window.dataLayer=window.dataLayer||[];window.gtag=window.gtag||function(){{dataLayer.push(arguments);}};if(['rockbarfxxkup.com','www.rockbarfxxkup.com'].includes(location.hostname)){{gtag('js',new Date());gtag('config','G-JPYT9JRWBT',{{allow_google_signals:false,allow_ad_personalization_signals:false}});const analyticsScript=document.createElement('script');analyticsScript.async=true;analyticsScript.src='https://www.googletagmanager.com/gtag/js?id=G-JPYT9JRWBT';document.head.appendChild(analyticsScript);}}</script>
<script src="/analytics.js" defer></script>
<meta property="og:type" content="website">
<meta property="og:site_name" content="Rock Bar FxxK Up">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{escape(canonical, quote=True)}">
<meta property="og:image" content="{ORIGIN}/assets/neon-social-preview.jpg">
<meta property="og:locale" content="{ {"en":"en_US","ja":"ja_JP","ko":"ko_KR","th":"th_TH","zh-Hans":"zh_CN"}[code] }">
<script type="application/ld+json">{schema}</script>
</head>
<body class="whisky-page">
<a class="skip" href="#main">{escape({"en":"Skip to content","ja":"本文へ移動","ko":"본문으로 이동","th":"ข้ามไปยังเนื้อหา","zh-Hans":"跳至正文"}[code])}</a>
<header class="whisky-header">
  <a class="brand" href="{escape(lang_root, quote=True)}" aria-label="Rock Bar FxxK Up home" data-track-event="whisky_home_click" data-track-destination="home" data-track-placement="whisky_logo"><img src="/assets/logo.svg" alt="Rock Bar FxxK Up" width="66" height="66"><span>SUSUKINO<br>SAPPORO, JP</span></a>
  <nav aria-label="Main navigation"><a href="{escape(lang_root, quote=True)}" data-track-event="whisky_home_click" data-track-destination="home" data-track-placement="whisky_navigation">{escape(label["home"])}</a><a href="{escape(lang_root + '#drinks', quote=True)}" data-track-event="whisky_drinks_click" data-track-destination="drinks_section" data-track-placement="whisky_navigation">{escape(label["drinks"])}</a><a href="{escape(lang_root + '#visit', quote=True)}" data-track-event="whisky_find_us_click" data-track-destination="visit_section" data-track-placement="whisky_navigation">{escape(label["find"])}</a></nav>
  <div class="header-actions"><details class="language-menu"><summary id="language">{escape(label["language"])}</summary><nav class="language-options" aria-label="{escape(label['languages'], quote=True)}">{language_options}</nav></details></div>
</header>
<main id="main">
  <section class="whisky-hero">
    <div class="section-tag">{escape(label["area"])}</div>
    <h1>{escape(inventory["heading"])}</h1>
    <p class="whisky-intro">{escape(inventory["description"])}</p>
    <p class="whisky-availability">{escape(label["availability"])}</p>
    {source_note}
  <div class="whisky-visit-links"><a href="/menu/" data-track-event="menu_open" data-track-destination="static_menu" data-track-placement="whisky_visit_links">{escape(label["full_menu"])} {external_icon}</a><a class="whisky-directions-button" href="https://maps.app.goo.gl/95hYVdZMdPot4WQy5" target="_blank" rel="noopener" data-track-event="whisky_directions_click" data-track-destination="google_maps" data-track-placement="whisky_visit_links">{escape(label["directions"])} {external_icon}</a></div>
  </section>
  <section class="whisky-catalog" aria-label="{escape(inventory['heading'], quote=True)}">
    <div class="whisky-controls" hidden>
      <label class="sr-only" for="whisky-search">{escape(label["search"])}</label>
      <input id="whisky-search" type="search" placeholder="{escape(label['placeholder'], quote=True)}" autocomplete="off">
      <label class="sr-only" for="whisky-category">{escape(label["category"])}</label>
      <div class="whisky-category-control">
        <select id="whisky-category">{"".join(category_options)}</select>
        <p id="whisky-count" data-suffix="{escape(label['count'], quote=True)}" aria-live="polite">({initial_count} {escape(label['count'])})</p>
      </div>
      <button id="whisky-clear" type="button">{escape(label["clear"])}</button>
    </div>
    <section id="whisky-empty" class="whisky-empty" aria-live="polite" hidden>
      <p class="whisky-empty-title">{escape(label["no_results"])}</p>
      <p>{escape(form_copy["empty_copy"])}</p>
      <form id="whisky-suggestion-form" class="whisky-suggestion" novalidate>
        <label for="whisky-suggestion">{escape(form_copy["suggestion_label"])}</label>
        <input id="whisky-suggestion" name="suggestion" type="text" maxlength="80" autocomplete="off" required>
        <p class="whisky-suggestion-note">{escape(form_copy["suggestion_note"])}</p>
        <label class="whisky-suggestion-consent"><input id="whisky-suggestion-certify" type="checkbox" required> {escape(form_copy["certify"])}</label>
        <button class="button yellow" type="submit">{escape(form_copy["submit"])}</button>
        <p id="whisky-suggestion-status" class="whisky-suggestion-status" role="status" aria-live="polite"><svg class="whisky-suggestion-status-icon" viewBox="0 0 48 32" aria-hidden="true"><rect x="4" y="5" width="15" height="23" rx="2"/><path d="M8 11h7M8 16h7M8 21h4M19 17h4"/><g class="whisky-gate-arm"><path d="M23 17h21"/><circle cx="23" cy="17" r="2"/></g></svg><span id="whisky-suggestion-message"></span></p>
      </form>
    </section>
    {"".join(category_sections)}
    <section class="whisky-map" aria-label="{escape(form_copy['map_label'], quote=True)}">
      <iframe src="https://storage.googleapis.com/maps-solutions-y33v72la8f/commutes/2na5/commutes.html" width="100%" height="420" style="border:0;" loading="lazy" title="{escape(form_copy['map_title'], quote=True)}"></iframe>
    </section>
  </section>
</main>
<nav class="language-links" aria-label="Website languages">{language_options}</nav>
<footer><span>© 2026 ROCK BAR FxxK UP</span><span>ROCK &amp; WHISKY. SUSUKINO, SAPPORO.</span><a href="{escape(privacy_href, quote=True)}" data-track-event="whisky_privacy_click" data-track-destination="privacy_policy" data-track-placement="whisky_footer">{escape(label["privacy"])}</a></footer>
<div class="mobile-bar"><a href="https://maps.app.goo.gl/95hYVdZMdPot4WQy5" target="_blank" rel="noopener" data-track-event="whisky_directions_click" data-track-destination="google_maps" data-track-placement="whisky_mobile_bar">{escape(label["directions"])} {external_icon}</a><a href="https://www.instagram.com/rockbar_fxxkup/" target="_blank" rel="noopener" data-track-event="whisky_instagram_click" data-track-destination="bar" data-track-placement="whisky_mobile_bar">{escape(label["instagram"])} {external_icon}</a></div>
</body>
</html>'''
    return body

def add_home_links(config):
    path = DIST / (config["folder"] + "/index.html" if config["folder"] else "index.html")
    text = path.read_text(encoding="utf-8")
    # build-seo.py creates every locale from the canonical homepage template,
    # which already contains the translated navigation link and primary CTA.
    # Older builds injected a second link because their route is locale-prefixed.
    text = re.sub(r'<a class="whisky-nav-link"[^>]*>.*?</a>', '', text, flags=re.DOTALL)
    text = re.sub(r'<a class="text-link whisky-index-link"[^>]*>.*?</a>', '', text, flags=re.DOTALL)
    path.write_text(text, encoding="utf-8")

def remove_home_links(config):
    path = DIST / (config["folder"] + "/index.html" if config["folder"] else "index.html")
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'<a class="whisky-nav-link"[^>]*>.*?</a>', '', text, flags=re.DOTALL)
    text = re.sub(r'<a class="text-link whisky-index-link"[^>]*>.*?</a>', '', text, flags=re.DOTALL)
    path.write_text(text, encoding="utf-8")

def write_sitemap():
    sitemap_ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    xhtml_ns = "http://www.w3.org/1999/xhtml"
    ET.register_namespace("", sitemap_ns)
    ET.register_namespace("xhtml", xhtml_ns)
    sitemap_path = DIST / "sitemap.xml"
    if sitemap_path.exists():
        root = ET.parse(sitemap_path).getroot()
    else:
        root = ET.Element("{" + sitemap_ns + "}urlset")
    existing = {
        node.find("{" + sitemap_ns + "}loc").text: node
        for node in root.findall("{" + sitemap_ns + "}url")
        if node.find("{" + sitemap_ns + "}loc") is not None
    }
    alternates = [(config["code"], page_url(config)) for config in ACTIVE_LANGUAGES]
    for config in ACTIVE_LANGUAGES:
        url = page_url(config)
        node = existing.get(url)
        if node is None:
            node = ET.SubElement(root, "{" + sitemap_ns + "}url")
            ET.SubElement(node, "{" + sitemap_ns + "}loc").text = url
        for alternate in node.findall("{" + xhtml_ns + "}link"):
            node.remove(alternate)
        for lang, alternate_url in alternates:
            ET.SubElement(node, "{" + xhtml_ns + "}link", {"rel":"alternate", "hreflang":lang, "href":alternate_url})
        ET.SubElement(node, "{" + xhtml_ns + "}link", {"rel":"alternate", "hreflang":"x-default", "href":page_url(ACTIVE_LANGUAGES[0])})
    sitemap_path.write_bytes(ET.tostring(root, encoding="utf-8", xml_declaration=True))
    (DIST / "robots.txt").write_text("User-agent: *\nAllow: /\n\nSitemap: " + ORIGIN + "/sitemap.xml\n", encoding="utf-8")

def main():
    inventories = {config["code"]: parse_inventory(config) for config in ACTIVE_LANGUAGES}
    menu_urls = {
        config["code"]: ("/" + (config["folder"] + "/" if config["folder"] else "") + "whisky/")
        if config in ACTIVE_LANGUAGES else locale_root(config)
        for config in LANGUAGES
    }
    for config in LANGUAGES:
        if config not in ACTIVE_LANGUAGES:
            if config["folder"]:
                shutil.rmtree(DIST / config["folder"] / "whisky", ignore_errors=True)
            remove_home_links(config)
            continue
        target = DIST / (config["folder"] + "/whisky/index.html" if config["folder"] else "whisky/index.html")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_page(config, inventories[config["code"]], menu_urls), encoding="utf-8")
        add_home_links(config)
    shutil.copyfile(ROOT / "source" / "whisky.js", DIST / "whisky.js")
    write_sitemap()
    import subprocess
    import sys
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build-menu.py")], check=True)
    print("Built all active localized whisky pages from the source inventories.")

if __name__ == "__main__":
    main()
