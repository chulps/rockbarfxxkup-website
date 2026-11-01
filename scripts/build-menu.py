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
    grouped = OrderedDict()
    for item in items:
        grouped.setdefault(item["category"], []).append(item)

    options = ['<option value="all">All categories</option>']
    sections = []
    list_items = []
    position = 0
    for category_id, (category, category_items) in enumerate(grouped.items(), 1):
        options.append(f'<option value="{category_id}">{escape(category)}</option>')
        rows = []
        for item in category_items:
            position += 1
            name = item["name"].strip()
            price = price_label(item.get("prices", {}))
            searchable = " ".join([
                name,
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
            '<h2 id="category-' + str(category_id) + '">' + escape(category) + '</h2>'
            '<ul class="whisky-list">' + "".join(rows) + '</ul></section>'
        )

    title = "Sapporo Bar Menu & Prices | Rock Bar FxxK Up"
    description = "Browse Rock Bar FxxK Up's full drinks menu and prices in Susukino, Sapporo. Search Japanese whisky, Scotch, bourbon, cocktails, beer and more."
    canonical = ORIGIN + "/menu/"
    schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": title,
        "description": description,
        "url": canonical,
        "inLanguage": "en",
        "isPartOf": {"@type": "WebSite", "name": "Rock Bar FxxK Up", "url": ORIGIN + "/"},
        "about": {"@type": "BarOrPub", "name": "Rock Bar FxxK Up", "url": ORIGIN + "/"},
        "mainEntity": {"@type": "ItemList", "numberOfItems": len(list_items), "itemListElement": list_items},
    }
    external_icon = '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19 19 5M5 5h14v14"></path></svg>'
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#161414">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description, quote=True)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{canonical}">
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
  <a class="brand" href="/" aria-label="Rock Bar FxxK Up home"><img src="/assets/logo.svg" alt="Rock Bar FxxK Up" width="66" height="66"><span>SUSUKINO<br>SAPPORO, JP</span></a>
  <nav aria-label="Main navigation"><a href="/">The bar</a><a href="/music/">Music</a><a href="/whisky/">Whisky</a><a href="/menu/" aria-current="page">Full menu</a></nav>
  <div class="header-actions"><a class="small-cta" href="https://www.instagram.com/rockbar_fxxkup/" target="_blank" rel="noopener" data-track-event="instagram_click" data-track-destination="bar" data-track-placement="menu_header">INSTAGRAM {external_icon}</a></div>
</header>
<main id="main">
  <section class="whisky-hero menu-hero">
    <div class="section-tag">ROCK &amp; WHISKY BAR / SUSUKINO, SAPPORO</div>
    <h1>SAPPORO BAR<br>MENU &amp; PRICES<span class="accent">.</span></h1>
    <p class="whisky-intro">Browse Rock Bar FxxK Up's full drinks menu in Susukino, Sapporo. Find Japanese whisky, Scotch, bourbon, cocktails, beer, soft drinks and more, with prices listed by pour or serving.</p>
    <p class="whisky-availability">¥500 cover charge (tax included) · One drink minimum</p>
    <p class="whisky-updated">Last updated November 1, 2026</p>
    <p class="whisky-availability">Prices are shown as listed. Items and availability may change.</p>
  </section>
  <section class="whisky-catalog menu-catalog" aria-label="Full drinks menu">
    <div class="whisky-controls menu-controls">
      <label class="sr-only" for="menu-search">Search the drinks menu</label>
      <input id="menu-search" type="search" placeholder="Search drinks, brands or styles" autocomplete="off">
      <label class="sr-only" for="menu-category">Category</label>
      <div class="whisky-category-control"><select id="menu-category">{"".join(options)}</select><p id="menu-count" aria-live="polite">({len(items)} drinks)</p></div>
      <button id="menu-clear" type="button">Clear</button>
    </div>
    <section id="menu-empty" class="whisky-empty" aria-live="polite" hidden><p class="whisky-empty-title">No drinks match that search.</p><p>Try a different name, category or style.</p></section>
    {"".join(sections)}
  </section>
</main>
<nav class="language-links" aria-label="Website languages"><a href="/" hreflang="en" lang="en">English</a><a href="/ja/" hreflang="ja" lang="ja">日本語</a><a href="/ko/" hreflang="ko" lang="ko">한국어</a><a href="/th/" hreflang="th" lang="th">ไทย</a><a href="/zh-hans/" hreflang="zh-Hans" lang="zh-Hans">简体中文</a></nav>
<footer><span>© 2026 ROCK BAR FxxK UP</span><span>ROCK &amp; WHISKY. SUSUKINO, SAPPORO.</span><a href="/privacy/#en">Privacy policy</a></footer>
<div class="mobile-bar"><a href="https://maps.app.goo.gl/95hYVdZMdPot4WQy5" target="_blank" rel="noopener" data-track-event="directions_click" data-track-destination="google_maps" data-track-placement="menu_mobile_bar">GET DIRECTIONS {external_icon}</a><a href="https://www.instagram.com/rockbar_fxxkup/" target="_blank" rel="noopener" data-track-event="instagram_click" data-track-destination="bar" data-track-placement="menu_mobile_bar">INSTAGRAM {external_icon}</a></div>
</body>
</html>'''
    target = DIST / "menu"
    target.mkdir(parents=True, exist_ok=True)
    (target / "index.html").write_text(html, encoding="utf-8")
    (target / "menu.js").write_text((SOURCE / "menu.js").read_text(encoding="utf-8"), encoding="utf-8")
    (target / "menu.css").write_text((SOURCE / "menu.css").read_text(encoding="utf-8"), encoding="utf-8")
    sitemap = DIST / "sitemap.xml"
    tree = ET.parse(sitemap)
    root = tree.getroot()
    ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    if not any(node.find("{" + ns + "}loc").text == canonical for node in root.findall("{" + ns + "}url")):
        node = ET.SubElement(root, "{" + ns + "}url")
        ET.SubElement(node, "{" + ns + "}loc").text = canonical
        tree.write(sitemap, encoding="utf-8", xml_declaration=True)
    print(f"Built static searchable menu with {len(items)} available priced items in {len(grouped)} categories.")


if __name__ == "__main__":
    main()
