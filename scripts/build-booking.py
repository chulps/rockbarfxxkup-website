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
        if re.search(r'(?<![\w-])placeholder="[^"]*"', tag):
            tag = re.sub(r'(?<![\w-])placeholder="[^"]*"', placeholder, tag, count=1)
        else:
            tag += " " + placeholder
        return tag + match.group(3)

    document = re.sub(r'(<[^>]*\bdata-copy-placeholder="([^"]+)"[^>]*)(>)', copy_placeholder, document)
    language_nav = {
        "en": "Website language",
        "ja": "ウェブサイトの言語",
        "ko": "웹사이트 언어",
        "th": "ภาษาเว็บไซต์",
        "zh-hans": "网站语言",
    }[code]
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


# Booking is temporarily hidden. Source/template/translation files are retained.
# See BOOKING-RESTORE.md before re-enabling the public form.
UNAVAILABLE = {
    "en": ("Online booking is temporarily unavailable", "Return to the homepage"),
    "ja": ("オンライン予約は現在ご利用いただけません", "ホームページに戻る"),
    "ko": ("온라인 예약을 일시적으로 이용할 수 없습니다", "홈페이지로 돌아가기"),
    "th": ("ขณะนี้ไม่สามารถจองออนไลน์ได้ชั่วคราว", "กลับไปยังหน้าแรก"),
    "zh-hans": ("在线预订暂时不可用", "返回首页"),
}


def build() -> None:
    # A disabled replacement prevents a cached copy of the old form from loading
    # a fresh request-submission script. Already-open pages and the API are separate.
    (DIST / "booking.js").write_text(
        '(() => { const form = document.querySelector("#reservation-form"); '
        'if (form) form.addEventListener("submit", e => e.preventDefault(), true); '
        '})();\n'
    )
    for code, (title, back) in UNAVAILABLE.items():
        lang = "zh-Hans" if code == "zh-hans" else code
        home = "/" if code == "en" else f"/{code}/"
        output = DIST / "book/index.html" if code == "en" else DIST / code / "book/index.html"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex, nofollow"><meta name="theme-color" content="#161414"><title>{escape(title)}</title><link rel="stylesheet" href="/style.css"></head>
<body><main style="max-width:48rem;margin:12vh auto;padding:2rem"><h1>{escape(title)}</h1><p><a href="{home}">{escape(back)}</a></p></main></body></html>
''')
    sitemap = DIST / "sitemap.xml"
    if sitemap.exists():
        sitemap_text = sitemap.read_text()
        # Remove only complete booking entries. Keep unrelated sitemap entries.
        sitemap_text = re.sub(r'<(?:ns0:)?url>\s*<(?:ns0:)?loc>https://www\.rockbarfxxkup\.com/(?:ja/|ko/|th/|zh-hans/)?book/</(?:ns0:)?loc>.*?</(?:ns0:)?url>', '', sitemap_text, flags=re.S)
        sitemap.write_text(sitemap_text)


if __name__ == "__main__":
    build()
