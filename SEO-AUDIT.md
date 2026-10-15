# SEO audit — 2026-10-15

Canonical origin: https://www.rockbarfxxkup.com/

## Findings addressed
- Added a crawl policy and sitemap discovery in robots.txt.
- Added an XML sitemap for the English homepage and Japanese /ja/ page.
- Added self-referencing canonical URLs and reciprocal en/ja/x-default hreflang annotations.
- Replaced old-host social metadata with custom-domain Open Graph and Twitter summary cards.
- Added localized titles and descriptions, social image dimensions/alt text, app manifest and Apple touch icon.
- Added JSON-LD BarOrPub, WebSite and WebPage entities with verified-on-page address, telephone, menu, Instagram and overnight opening hours. No invented coordinates, review counts or self-serving rating markup.
- Pre-rendered Japanese HTML and added crawlable language links. English and Japanese no longer depend on navigator language or saved state for initial content; Korean, Thai and Chinese remain interactive choices, not separately indexed pages.
- Fixed carousel asset paths for nested language routes.
- Added intrinsic image dimensions and asynchronous decoding while preserving lazy loading and the priority hero image.

## Validation
- scripts/check-seo.py validates canonical URLs, alternates, metadata uniqueness, JSON-LD parsing, local assets, menu destination, image dimensions, sitemap XML and robots directive.
- node --check dist/app.js passes.
- scripts/build-seo.py regenerates pages and SEO assets from source/index.html.

## Remaining external checks / account work
- Live fetches unavailable from this execution environment; no Lighthouse, Core Web Vitals, visual browser or Google Rich Results Test score claimed.
- Verify the domain in Google Search Console, submit /sitemap.xml and inspect English/Japanese URLs.
- Add the new website and interactive menu to the Google Business Profile through the owner's account.
- Canonical tags consolidate duplicate hosts as a hint; server-side redirects from non-www and the original ChatGPT hostname have not been configured or verified.
- Korean, Thai and Chinese translations require a completeness review before publishing independent indexable pages.
- No analytics or Search Console verification ID was invented or added.
