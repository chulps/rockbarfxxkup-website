"""Build localized booking pages using only the Python standard library."""
from html import escape
from pathlib import Path
import json
import re


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
ORIGIN = "https://www.rockbarfxxkup.com"
COPY = json.loads((ROOT / "source/booking-translations.json").read_text())
TEMPLATE = (ROOT / "source/booking.html").read_text()
LANGUAGES = {"en": "English", "ja": "日本語", "ko": "한국어", "th": "ไทย", "zh-hans": "简体中文"}


def render(code: str, messages: dict[str, str], pages: dict[str, str]) -> str:
    document = TEMPLATE
    lang = "zh-Hans" if code == "zh-hans" else code
    document = document.replace('<html lang="en">', f'<html lang="{lang}">', 1)
    document = document.replace('<body data-locale="en">', f'<body data-locale="{code}">', 1)
    home_url = "/" if code == "en" else f"/{code}/"
    document = document.replace('href="/"', f'href="{home_url}"')
    document = document.replace('href="/#visit"', f'href="{home_url}#visit"')
    document = re.sub(r"(<title>).*?(</title>)", lambda m: m[1] + escape(messages["titleTag"]) + m[2], document, count=1, flags=re.S)
    document = re.sub(
        r'(<meta\s+name="description"\s+content=")[^"]*("\s*/?>)',
        lambda m: m[1] + escape(messages["description"], quote=True) + m[2], document, count=1,
    )

    def copy_text(match: re.Match[str]) -> str:
        key = match.group(2)
        value = messages.get(key)
        if value is None:
            return match.group(0)
        return match.group(1) + escape(value)

    document = re.sub(r'(<[^>]*\bdata-copy="([^"]+)"[^>]*>)([^<]*)', copy_text, document)

    def copy_placeholder(match: re.Match[str]) -> str:
        key = match.group(2)
        value = messages.get(key)
        if value is None:
            return match.group(0)
        tag = match.group(1)
        placeholder = f'placeholder="{escape(value, quote=True)}"'
        if re.search(r'\bplaceholder="[^"]*"', tag):
            tag = re.sub(r'\bplaceholder="[^"]*"', placeholder, tag, count=1)
        else:
            tag += " " + placeholder
        return tag + match.group(3)

    document = re.sub(r'(<[^>]*\bdata-copy-placeholder="([^"]+)"[^>]*)(>)', copy_placeholder, document)
    language_nav = "Website language" if code == "en" else "ウェブサイトの言語"
    document = re.sub(r'(<div\s+class="language-links"\s+aria-label=")[^"]*(")', lambda m: m[1] + language_nav + m[2], document, count=1)

    for language in LANGUAGES:
        href = "/book/" if language == "en" else f"/{language}/book/"

        def update_link(match: re.Match[str]) -> str:
            tag = match.group(0)
            tag = re.sub(r'\bhref="[^"]*"', f'href="{href}"', tag, count=1)
            tag = re.sub(r'\s+aria-current="page"', "", tag)
            if language == code:
                tag = tag[:-1] + ' aria-current="page">'
            return tag

        document = re.sub(rf'<a\b[^>]*\blang="{re.escape("zh-Hans" if language == "zh-hans" else language)}"[^>]*>', update_link, document, count=1)

    alternates = [f'<link rel="canonical" href="{pages[code]}">']
    alternates.extend(
        f'<link rel="alternate" hreflang="{"zh-Hans" if language == "zh-hans" else language}" href="{url}">'
        for language, url in pages.items()
    )
    alternates.append(f'<link rel="alternate" hreflang="x-default" href="{pages["en"]}">')
    document = document.replace("</head>", "\n  " + "\n  ".join(alternates) + "\n</head>", 1)
    json_data = json.dumps(messages, ensure_ascii=False).replace("</", "<\\/")
    document = document.replace("</body>", f'<script id="booking-messages" type="application/json">{json_data}</script>\n</body>', 1)
    return "<!doctype html>\n" + document


def build() -> None:
    (DIST / "booking.css").write_text((ROOT / "source/booking.css").read_text())
    (DIST / "booking.js").write_text((ROOT / "source/booking.js").read_text())
    pages = {code: ORIGIN + ("/book/" if code == "en" else f"/{code}/book/") for code in COPY}
    for code, messages in COPY.items():
        output = DIST / "book/index.html" if code == "en" else DIST / code / "book/index.html"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render(code, messages, pages))

    sitemap = DIST / "sitemap.xml"
    sitemap_text = sitemap.read_text()
    existing = set(re.findall(r"<ns0:loc>(.*?)</ns0:loc>", sitemap_text))
    entries = "".join(
        f"<ns0:url><ns0:loc>{url}</ns0:loc></ns0:url>"
        for url in pages.values() if url not in existing
    )
    if entries:
        sitemap.write_text(sitemap_text.replace("</ns0:urlset>", entries + "</ns0:urlset>", 1))


if __name__ == "__main__":
    build()
