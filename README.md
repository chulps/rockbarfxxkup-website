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

## The autonomous A/B and SEO workflow

The experiment runs in two layers. The site assigns and remembers a 50/50 variant in the visitor’s browser, serves localized copy, and records exposure after the hero is seen. A fixed-horizon analysis joins mature GA4 events with the BigQuery export, checks data coverage and experiment guardrails, and makes a deterministic promote, retain, or inconclusive decision. Weekly SEO collection also reads Search Console and public sitemap pages.

The scheduled Codex workflow reviews aggregate evidence and can apply a verified decision, make bounded site changes, and publish through the existing Sites project under the owner’s standing authorization. Python does the collection and statistics; no separate LLM API is called by the collector. It does not optimize toward a winner from weekly peeks: the test plan sets the window and gates in advance, and insufficient evidence keeps the current copy. See [`automation/README.md`](automation/README.md), [`automation/OPTIMIZER.md`](automation/OPTIMIZER.md), [`automation/weekly.py`](automation/weekly.py), and [`automation/decision.py`](automation/decision.py).

## Connected measurement sources

| Source | What the project reads or records | Connection and limits |
| --- | --- | --- |
| **Google Analytics 4 (GA4)** | Site page and action events; traffic channels, language, landing pages, named events, and sessions tagged for Google Business Profile links. | Site measurement ID `G-JPYT9JRWBT`; Data API property `559070143`. Read-only reporting. Tagged GBP sessions describe website activity only. |
| **Google Search Console** | Clicks, impressions, CTR, average position, and query/page/country/device rows for the verified domain property. | Webmasters API with read-only scope for `sc-domain:rockbarfxxkup.com`. This collector reports search performance; it does not request URL indexing. |
| **Google BigQuery** | GA4 exported event rows used to build mature A/B cohorts and apply the predeclared decision rules. | Read-only project `chuck-tech`, dataset `analytics_559070143`, location `asia-northeast1`. Visitor identifiers are used in memory for cohort joins; saved reports contain aggregate experiment results. |
| **Google Business Profile (GBP)** | Optional, separately labeled snapshot of profile views, calls, directions, website clicks, or menu actions when a validated export is supplied. | Native Business Profile Performance API access is **not connected**: the documented application was rejected and the current OAuth grant lacks `business.manage`. The project separately reports GA4 sessions tagged `google_business_profile`; those are not Maps/Search profile metrics. No fresh GBP snapshot is bundled here. |
| **BarTicket menu export** | Static source data for the searchable menu’s 280 listed drinks, categories, and yen prices. | Imported from the supplied JSON into [`source/menu/menu-data.json`](source/menu/menu-data.json); it is not a live BarTicket API connection. |

The analytics and Search Console OAuth grants are read-only; BigQuery uses a separate read-only grant. Token files and OAuth client configuration are stored in the owner’s local configuration directory, outside this repository. Private run reports are written under ignored `reports/` and are not part of the public site or this GitHub repository. Source code and operational notes for these connections live in [`automation/pilot.py`](automation/pilot.py), [`automation/bigquery_events.py`](automation/bigquery_events.py), and [`automation/weekly.py`](automation/weekly.py).

## Built with

- Static HTML, CSS, and JavaScript
- Python build scripts for localized pages, metadata, sitemap, and menu generation
- GA4 web events and read-only GA4 / Search Console / BigQuery reporting
- Scheduled SEO and experiment workflow with bounded publishing through Sites
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
