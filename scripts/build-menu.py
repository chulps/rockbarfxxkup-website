from collections import OrderedDict
from html import escape
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "menu"
DIST = ROOT / "dist"
ORIGIN = "https://www.rockbarfxxkup.com"
LOCALES = {"en": "en", "ja": "ja", "ko": "ko", "th": "th", "zh-hans": "zh-Hans"}


def key(value):
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def inventory_translations(locale):
    english_file = ROOT / "source" / "whisky" / "whisky-inventory.md"
    source_file = ROOT / "source" / "whisky" / ("whisky-inventory.md" if locale == "en" else f"whisky-inventory-{locale}.md")

    def names(path):
        result = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("- "):
                result.append(line[2:].split(" — ", 1)[0].strip())
        return result

    english = names(english_file)
    translated = names(source_file)
    return {key(original): translated_name for original, translated_name in zip(english, translated)}


def price_label(prices):
    pours = []
    for size in ("15ml", "30ml"):
        value = prices.get(size)
        if value:
            pours.append(f"{size} ¥{value:,}")
    standard = prices.get("standard")
    if standard:
        pours.append(f"¥{standard:,}")
    return " / ".join(pours)


def main():
    items = json.loads((SOURCE / "menu-data.json").read_text(encoding="utf-8"))
    i18n = json.loads((SOURCE / "menu-i18n.json").read_text(encoding="utf-8"))
    grouped = OrderedDict()
    for item in items:
        grouped.setdefault(item["category"], []).append(item)
    external_icon = '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19 19 5M5 5h14v14"></path></svg>'
    schema_menus = {}

    for locale, html_language in LOCALES.items():
        content = i18n.get(locale)
        inventory_names = inventory_translations(locale)
        categories = content.get("categories", {}) if content else {}
        translated_items = content.get("items", {}) if content else {}

        def display_name(english_name):
            if locale == "en":
                return english_name
            return inventory_names.get(key(english_name), translated_items.get(english_name, english_name))

        def display_category(english_category):
            return categories.get(english_category, english_category) if content else english_category

        all_label = content["all"] if content else "All categories"
        options = [f'<option value="all">{escape(all_label)}</option>']
        sections = []
        list_items = []
        position = 0
        for category_id, (category, category_items) in enumerate(grouped.items(), 1):
            translated_category = display_category(category)
            options.append(f'<option value="{category_id}">{escape(translated_category)}</option>')
            rows = []
            for item in category_items:
                position += 1
                original_name = item["name"].strip()
                name = display_name(original_name)
                price = price_label(item.get("prices", {}))
                searchable = " ".join([
                    name,
                    original_name,
                    translated_category,
                    category,
                    item.get("subcategory", ""),
                    " ".join(item.get("tags", [])),
                ]).strip()
                rows.append(
                    '<li class="whisky-item menu-item" data-search="' + escape(searchable, quote=True) + '">'
                    '<span class="whisky-name menu-item-name">' + escape(name) + '</span>'
                    '<span class="whisky-price menu-item-price">' + escape(price) + '</span>'
                    '</li>'
                )
                list_items.append({"@type": "ListItem", "position": position, "name": name})
            sections.append(
                '<section class="whisky-category menu-category" data-menu-group data-category-id="' + str(category_id) + '">'
                '<h2 id="category-' + str(category_id) + '">' + escape(translated_category) + '</h2>'
                '<ul class="whisky-list">' + "".join(rows) + '</ul></section>'
            )

        if locale == "en":
            title = "Sapporo Bar Menu & Prices | Rock Bar FxxK Up"
            description = "Browse Rock Bar FxxK Up's full drinks menu and prices in Susukino, Sapporo. Search Japanese whisky, Scotch, bourbon, cocktails, beer and more."
            canonical = ORIGIN + "/menu/"
            copy = {
                "tag": "ROCK & WHISKY BAR / SUSUKINO, SAPPORO",
                "h1": "SAPPORO BAR<br>MENU &amp; PRICES",
                "intro": "Browse Rock Bar FxxK Up's full drinks menu in Susukino, Sapporo. Find Japanese whisky, Scotch, bourbon, cocktails, beer, soft drinks and more, with prices listed by pour or serving.",
                "cover": "¥500 cover charge (tax included) · One drink minimum",
                "updated": "Last updated November 1, 2026",
                "availability": "Prices are shown as listed. Items and availability may change.",
                "search": "Search drinks, brands or styles",
                "clear": "Clear",
                "emptyTitle": "No drinks match that search.",
                "emptyText": "Try a different name, category or style.",
                "home": "The bar", "music": "Music", "whisky": "Whisky", "fullMenu": "Full menu", "directions": "GET DIRECTIONS",
                "countSingular": "drink", "countPlural": "drinks", "countSpace": "true"
            }
        else:
            title = content["title"]
            description = content["description"]
            canonical = ORIGIN + f"/{locale}/menu/"
            copy = content
            copy["countSpace"] = "true" if locale == "th" else "false"

        schema_menus[locale] = canonical
        schema = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": title,
            "description": description,
            "url": canonical,
            "inLanguage": html_language,
            "isPartOf": {"@type": "WebSite", "name": "Rock Bar FxxK Up", "url": ORIGIN + "/"},
            "about": {"@type": "BarOrPub", "name": "Rock Bar FxxK Up", "url": ORIGIN + "/"},
            "mainEntity": {"@type": "ItemList", "numberOfItems": len(list_items), "itemListElement": list_items},
        }
        nav_home = "/" if locale == "en" else f"/{locale}/"
        nav_music = "/music/" if locale == "en" else f"/{locale}/music/"
        nav_whisky = "/whisky/" if locale == "en" else f"/{locale}/whisky/"
        nav_menu = "/menu/" if locale == "en" else f"/{locale}/menu/"
        count_unit_singular = copy.get("countSingular", copy.get("countPlural", "drinks"))
        count_unit_plural = copy.get("countPlural", "drinks")
        count_unit_space = copy.get("countSpace", "true")
        count_initial_unit = count_unit_plural
        menu_description = "Full drinks menu" if locale == "en" else copy["fullMenu"]
        language = html_language
        category_label = "Category" if locale == "en" else {"ja": "カテゴリー", "ko": "종류", "th": "ประเภท", "zh-hans": "类别"}[locale]
        main_nav = "Main navigation" if locale == "en" else {"ja": "メインナビゲーション", "ko": "주 메뉴", "th": "เมนูหลัก", "zh-hans": "主导航"}[locale]
        strapline = "ROCK &amp; WHISKY. SUSUKINO, SAPPORO." if locale == "en" else {"ja": "ロックとウイスキー。すすきの・札幌。", "ko": "록과 위스키. 삿포로 스스키노.", "th": "ร็อกและวิสกี้ ซูซูกิโนะ ซัปโปโร", "zh-hans": "摇滚与威士忌。札幌薄野。"}[locale]
        language_links = []
        for path_locale, hreflang, label in (("en", "en", "English"), ("ja", "ja", "日本語"), ("ko", "ko", "한국어"), ("th", "th", "ไทย"), ("zh-hans", "zh-Hans", "简体中文")):
            href = "/menu/" if path_locale == "en" else f"/{path_locale}/menu/"
            current = ' aria-current="page"' if path_locale == locale else ""
            language_links.append(f'<a href="{href}" hreflang="{hreflang}" lang="{hreflang}"{current}>{label}</a>')
        language_links_html = "".join(language_links)
        alternates_html = "".join(
            f'<link rel="alternate" hreflang="{hreflang}" href="{url}">'
            for hreflang, url in (("en", ORIGIN+"/menu/"), ("ja", ORIGIN+"/ja/menu/"), ("ko", ORIGIN+"/ko/menu/"), ("th", ORIGIN+"/th/menu/"), ("zh-Hans", ORIGIN+"/zh-hans/menu/"))
        )
        html = f'''<!doctype html>
<html lang="{language}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#161414">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description, quote=True)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{canonical}">
{alternates_html}
<link rel="icon" href="/assets/logo.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800;900&amp;family=DM+Sans:wght@400;500;600;700&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
<link rel="stylesheet" href="/menu/menu.css">
<script src="/analytics.js" defer></script>
<script src="/menu/menu.js" defer></script>
<script>window.dataLayer=window.dataLayer||[];window.gtag=window.gtag||function(){{dataLayer.push(arguments);}};if(['rockbarfxxkup.com','www.rockbarfxxkup.com'].includes(location.hostname)){{gtag('js',new Date());gtag('config','G-JPYT9JRWBT',{{allow_google_signals:false,allow_ad_personalization_signals:false}});const analyticsScript=document.createElement('script');analyticsScript.async=true;analyticsScript.src='https://www.googletagmanager.com/gtag/js?id=G-JPYT9JRWBT';document.head.appendChild(analyticsScript);}}</script>
<meta property="og:type" content="website">
<meta property="og:site_name" content="Rock Bar FxxK Up">
<meta property="og:title" content="{escape(title, quote=True)}">
<meta property="og:description" content="{escape(description, quote=True)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{ORIGIN}/assets/neon-social-preview.jpg">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace('</', '<\\/')}</script>
</head>
<body class="menu-page whisky-page">
<a class="skip" href="#main">Skip to content</a>
<header class="whisky-header">
  <a class="brand" href="{nav_home}" aria-label="Rock Bar FxxK Up"><img src="/assets/logo.svg" alt="Rock Bar FxxK Up" width="66" height="66"><span>SUSUKINO<br>SAPPORO, JP</span></a>
  <nav aria-label="{escape(main_nav)}"><a href="{nav_home}">{escape(copy['home'])}</a><a href="{nav_music}">{escape(copy['music'])}</a><a href="{nav_whisky}">{escape(copy['whisky'])}</a><a href="{nav_menu}" aria-current="page">{escape(copy['fullMenu'])}</a></nav>
  <div class="header-actions"><a class="small-cta" href="https://www.instagram.com/rockbar_fxxkup/" target="_blank" rel="noopener" data-track-event="instagram_click" data-track-destination="bar" data-track-placement="menu_header">INSTAGRAM {external_icon}</a></div>
</header>
<main id="main">
  <section class="whisky-hero menu-hero">
    <div class="section-tag">{copy['tag']}</div>
    <h1>{copy['h1']}<span class="accent">.</span></h1>
    <p class="whisky-intro">{escape(copy['intro'])}</p>
    <p class="whisky-availability">{escape(copy['cover'])}</p>
    <p class="whisky-updated">{escape(copy['updated'])}</p>
    <p class="whisky-availability">{escape(copy['availability'])}</p>
  </section>
  <section class="whisky-catalog menu-catalog" aria-label="{escape(menu_description)}">
    <div class="whisky-controls menu-controls">
      <label class="sr-only" for="menu-search">{escape(copy['search'])}</label>
      <input id="menu-search" type="search" placeholder="{escape(copy['search'], quote=True)}" autocomplete="off">
      <label class="sr-only" for="menu-category">{escape(category_label)}</label>
      <div class="whisky-category-control"><select id="menu-category" aria-label="{escape(all_label, quote=True)}">{"".join(options)}</select><p id="menu-count" data-unit-singular="{escape(count_unit_singular, quote=True)}" data-unit-plural="{escape(count_unit_plural, quote=True)}" data-unit-space="{count_unit_space}" aria-live="polite">({len(items)}{(' ' if count_unit_space == 'true' else '')}{escape(count_initial_unit)})</p></div>
      <button id="menu-clear" type="button">{escape(copy['clear'])}</button>
    </div>
    <section id="menu-empty" class="whisky-empty" aria-live="polite" hidden><p class="whisky-empty-title">{escape(copy['emptyTitle'])}</p><p>{escape(copy['emptyText'])}</p></section>
    {"".join(sections)}
  </section>
</main>
<nav class="language-links" aria-label="Website languages">{language_links_html}</nav>
<footer><span>© 2026 ROCK BAR FxxK UP</span><span>{strapline}</span><a href="/privacy/#{'ja' if locale == 'ja' else 'en'}">{'プライバシーポリシー' if locale == 'ja' else 'Privacy policy' if locale == 'en' else '개인정보 처리방침' if locale == 'ko' else 'นโยบายความเป็นส่วนตัว' if locale == 'th' else '隐私政策'}</a></footer>
<div class="mobile-bar"><a href="https://maps.app.goo.gl/95hYVdZMdPot4WQy5" target="_blank" rel="noopener" data-track-event="directions_click" data-track-destination="google_maps" data-track-placement="menu_mobile_bar">{escape(copy['directions'])} {external_icon}</a><a href="https://www.instagram.com/rockbar_fxxkup/" target="_blank" rel="noopener" data-track-event="instagram_click" data-track-destination="bar" data-track-placement="menu_mobile_bar">INSTAGRAM {external_icon}</a></div>
</body>
</html>'''
        target = DIST / ("menu" if locale == "en" else f"{locale}/menu")
        target.mkdir(parents=True, exist_ok=True)
        (target / "index.html").write_text(html, encoding="utf-8")
        (target / "menu.js").write_text((SOURCE / "menu.js").read_text(encoding="utf-8"), encoding="utf-8")
        (target / "menu.css").write_text((SOURCE / "menu.css").read_text(encoding="utf-8"), encoding="utf-8")
    sitemap = DIST / "sitemap.xml"
    tree = ET.parse(sitemap)
    root = tree.getroot()
    ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    for node in list(root.findall("{" + ns + "}url")):
        loc = node.find("{" + ns + "}loc")
        if loc is not None and "/menu/" in loc.text:
            root.remove(node)
    for locale, url in schema_menus.items():
        node = ET.SubElement(root, "{" + ns + "}url")
        ET.SubElement(node, "{" + ns + "}loc").text = url
        for hreflang, alternate in schema_menus.items():
            code = "zh-Hans" if hreflang == "zh-hans" else hreflang
            ET.SubElement(node, "{http://www.w3.org/1999/xhtml}link", rel="alternate", hreflang=code, href=alternate)
        ET.SubElement(node, "{http://www.w3.org/1999/xhtml}link", rel="alternate", hreflang="x-default", href=schema_menus["en"])
    tree.write(sitemap, encoding="utf-8", xml_declaration=True)
    print(f"Built searchable menus in five languages with {len(items)} available priced items in {len(grouped)} categories.")


if __name__ == "__main__":
    main()
