# ROCK BAR FxxK UP

<div align="center">

### ROCK · WHISKY · GOOD COMPANY

**The digital home of Rock Bar FxxK Up — a late-night rock and whisky bar in Susukino, Sapporo.**

[Visit the website](https://www.rockbarfxxkup.com/) · [Browse the full drinks menu](https://www.rockbarfxxkup.com/menu/) · [Explore the whisky list](https://www.rockbarfxxkup.com/whisky/) · [Discover the music](https://www.rockbarfxxkup.com/music/)

`5 LANGUAGES` &nbsp; `SEARCHABLE MENU` &nbsp; `SEO BUILT IN` &nbsp; `LIVE EXPERIMENTATION`

</div>

---

## The project

This repository powers the public website for **Rock Bar FxxK Up**, on the sixth floor in Susukino, Sapporo. It is a lightweight, statically generated site designed to help people find the bar, understand what is on offer, and feel comfortable visiting—whether they speak English, Japanese, Korean, Thai, or Simplified Chinese.

The site brings together the bar’s story, music, whisky collection, searchable drinks menu, practical visit details, and localized pages. Menu prices and products come from the supplied BarTicket menu data; availability can change.

## Every page, one click away

### English

| Page | Link |
| --- | --- |
| Home | [rockbarfxxkup.com](https://www.rockbarfxxkup.com/) |
| Music | [Music at the bar](https://www.rockbarfxxkup.com/music/) |
| Whisky | [Whisky list](https://www.rockbarfxxkup.com/whisky/) |
| Drinks menu | [Search the full menu](https://www.rockbarfxxkup.com/menu/) |
| Privacy | [Privacy policy](https://www.rockbarfxxkup.com/privacy/) |

### 日本語

| ページ | リンク |
| --- | --- |
| ホーム | [Rock Bar FxxK Up](https://www.rockbarfxxkup.com/ja/) |
| 音楽 | [店内の音楽](https://www.rockbarfxxkup.com/ja/music/) |
| ウイスキー | [ウイスキーリスト](https://www.rockbarfxxkup.com/ja/whisky/) |
| ドリンクメニュー | [全ドリンクメニュー](https://www.rockbarfxxkup.com/ja/menu/) |

### 한국어

| 페이지 | 링크 |
| --- | --- |
| 홈 | [Rock Bar FxxK Up](https://www.rockbarfxxkup.com/ko/) |
| 음악 | [바의 음악](https://www.rockbarfxxkup.com/ko/music/) |
| 위스키 | [위스키 리스트](https://www.rockbarfxxkup.com/ko/whisky/) |
| 음료 메뉴 | [전체 음료 메뉴](https://www.rockbarfxxkup.com/ko/menu/) |

### ไทย

| หน้า | ลิงก์ |
| --- | --- |
| หน้าแรก | [Rock Bar FxxK Up](https://www.rockbarfxxkup.com/th/) |
| ดนตรี | [ดนตรีในบาร์](https://www.rockbarfxxkup.com/th/music/) |
| วิสกี้ | [รายการวิสกี้](https://www.rockbarfxxkup.com/th/whisky/) |
| เมนูเครื่องดื่ม | [เมนูเครื่องดื่มทั้งหมด](https://www.rockbarfxxkup.com/th/menu/) |

### 简体中文

| 页面 | 链接 |
| --- | --- |
| 首页 | [Rock Bar FxxK Up](https://www.rockbarfxxkup.com/zh-hans/) |
| 音乐 | [酒吧音乐](https://www.rockbarfxxkup.com/zh-hans/music/) |
| 威士忌 | [威士忌酒单](https://www.rockbarfxxkup.com/zh-hans/whisky/) |
| 饮品菜单 | [完整饮品菜单](https://www.rockbarfxxkup.com/zh-hans/menu/) |

## Searchable menu

The drinks menu is generated from structured source data, so every listing remains crawlable without requiring a search or filter interaction. Visitors can search across 280 menu entries and filter by category. Search recognizes localized product names as well as their source names, while the visible menu stays in the selected language. Prices are shown in yen and by serving size where applicable.

## SEO, built into the pages

The goal is to make the right page useful for the right search—not to repeat keywords mechanically. The site organizes distinct intent into focused pages:

- **Home:** Rock Bar FxxK Up, rock and whisky in Susukino, Sapporo.
- **Whisky:** Japanese whisky, Scotch, bourbon, and the bar’s current whisky list and prices.
- **Menu:** the full Sapporo bar menu, with searchable drinks, brands, categories, and prices.
- **Music:** the rock, punk, and metal identity of the bar, song requests, and the people behind the playlists.

The build publishes language-specific titles and descriptions, canonical URLs, reciprocal `hreflang` links (including `x-default`), a sitemap, crawl rules, and structured data. Each language has a stable route and pre-rendered page content so search engines and visitors can reach it directly.

## The autonomous A/B test

The site includes an automated, first-visit confidence experiment. When enabled, a visitor’s browser assigns and remembers a 50/50 variant, serves localized copy, and records an exposure only after the hero is actually seen. Relevant clicks can then be attributed to the exposed variant.

The automation handles assignment and measurement; **it does not declare a winner or rewrite/publish the site by itself**. Results need human review, enough data, and a deliberate release decision. GA4 event instrumentation is configured for the experiment and site actions; confirm that events are arriving in the GA4 property before drawing conclusions from reports. Experiment configuration and operating notes are in [`source/experiments.json`](source/experiments.json) and [`EXPERIMENTS.md`](EXPERIMENTS.md).

## Built with

- Static HTML, CSS, and JavaScript
- Python build scripts for localized pages, metadata, sitemap, and menu generation
- GA4 event instrumentation for navigation and conversion intent
- Five locales: English, Japanese, Korean, Thai, and Simplified Chinese

## Build locally

```bash
python3 scripts/build-seo.py
```

The generated website is written to `dist/`. Menu source data and translations live under `source/menu/`; whisky lists and their translations live under `source/whisky/`.

---

<div align="center">

**ROCK BAR FxxK UP** · Susukino, Sapporo · [rockbarfxxkup.com](https://www.rockbarfxxkup.com/)

</div>
