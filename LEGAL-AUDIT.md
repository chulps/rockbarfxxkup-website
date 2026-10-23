# Website legal review — 23 October 2026

Scope: production v28 source 1a1c106b8eba6fc99d6b2c642123dfdbcd036224. Informational physical bar website, five languages; no on-site alcohol sales, checkout, accounts or inquiry forms. External menu inspected read-only; no BarTicket code changed.

## Findings and classification

- **Law:** drinking age remains 20. Serving under-20 customers knowingly is prohibited; age checks belong at service. NTA's online mail-order age fields/warnings apply to alcohol sales, not a blocking gate for this informational bar site. No blocking age gate added.
- **Industry guidance:** alcohol advertising self-regulation calls for clear 20+ messaging in internet advertising. Added the requested bilingual 20+/no drink-driving notice to all homepages and the privacy page. This notice supports responsible advertising; it does not replace on-premises age checks.
- **Law (APPI, as applicable):** specify/disclose purposes; protect personal information; provide procedures for rights requests and information about retained personal data; assess consent/safeguards for relevant third-party and overseas personal-data provision. Cookie identifiers are not automatically personal information in every context, and Article 31 depends on recipient identification circumstances. Do not assume a privacy notice alone authorizes every transfer.
- **Google contractual policy:** Analytics use and Google's collection/processing must be disclosed. Added a bilingual policy covering actual GA4 actions, identifiers, external fonts/hosting, browser storage, contact data, choices, retention, rights and updates. GA4 site configuration already disables Google signals and advertising personalization signals; unchanged.
- **Consent assessment:** no blanket Japanese prior-consent rule triggered merely by the present GA4 installation was established. No User-ID, customer upload, ad remarketing implementation or sensitive-data form found. No precautionary consent banner added. This is a Japan-focused assessment, not a determination of all overseas laws. Reassess if overseas ad targeting, identified-user data sharing, ad features or online sales are added.
- **Law (consumer price display, where taxable):** advertised prices must show the tax-inclusive final amount. A plain ¥500 can already be inclusive; lack of the word 税込 alone does not establish a violation. No amount or tax treatment invented.
- **Not currently applicable on observed site:** online alcohol-sale application fields and mail-order sales disclosures. The website links to a menu but does not accept sales/orders/payments.

## Implementation

- One indexable bilingual `/privacy/` page; Japanese and English section anchors and language tags; existing brand CSS, responsive readable layout, keyboard focus styles, metadata, canonical www URL and social metadata.
- Footer policy link and exact bilingual responsible-drinking notice on every locale.
- Sitemap gains only the canonical privacy URL; existing five homepages, hreflang, robots and canonical host retained.
- No new tracking event names. `analytics.js`, `app.js`, `experiments.js` and experiment configuration preserved byte-for-byte. Old directions/footer B winners and active persistent 50/50 first-visit test retained; no experiment exposure/assignment on the privacy page.
- GA4 administration inspected read-only: Rock Bar Fxxk Up property 559070143, event retention **2 months**, user retention **14 months**, reset on new user activity **enabled**. No settings/history changed. Policy records these observed values and date.

## Owner checks still needed

1. **Resolved 24 October 2026:** owner confirmed ¥500 is the final tax-inclusive cover charge, with no additional fee added to that charge. Both published mentions now explicitly say tax included in all five languages. The one-drink minimum remains unchanged. This confirmation applies to the cover charge; external menu tax treatment remains unconfirmed.
2. Public external menu has a Japanese Nikka Extra Marriage entry at **¥0**, while a separate English item lists 15 ml ¥1,200 / 30 ml ¥2,300. Also has **Custom cocktail (adjust price)** at ¥1,000 with an adjustment note. Confirm actual price/conditions and tax-inclusive totals in that app. Main website publishes no drink-package, extension or exclusion terms to verify. If such offers are advertised later, state final totals, duration, extension rules and exclusions clearly.
3. Confirm the legal proprietor/entity and representative (if a company), and the operational handling/retention/safeguards for phone/Instagram inquiries. The policy uses the verified trading name, existing store address and public contact channels; no corporate registration or private contact details invented. APPI retained-personal-data operator details must be available as applicable, including on request where allowed.
4. GA4 contractual/data-sharing/overseas safeguard arrangements and provider log retention cannot be established from front-end code alone. Verify actual arrangements where personal data provision rules apply. The policy does not assert all data are anonymous or that a notice itself supplies consent.

## Primary sources

- NTA drinking age / bar obligations: https://www.nta.go.jp/publication/pamph/koho/campaign/r8/Apr/05.htm
- NTA alcohol age-label notice (including online mail-order scope): https://www.nta.go.jp/taxes/sake/hyoji/miseinen/kokuji891122/01.htm
- Alcohol industry voluntary advertising standards: https://www.rcaa.jp/standard/koukoku.html and https://www.rcaa.jp/standard/pdf/jishukijun.pdf
- PPC APPI general guidelines: https://www.ppc.go.jp/personalinfo/legal/guidelines_tsusoku/
- PPC Q&A (including cookies/personal-related information and tags, Q8): https://www.ppc.go.jp/personalinfo/faq/APPI_QA/
- PPC overseas provision guidelines: https://www.ppc.go.jp/personalinfo/legal/guidelines_offshore/
- NTA tax-inclusive price display: https://www.nta.go.jp/taxes/shiraberu/taxanswer/shohi/6902.htm
- Google Analytics disclosure policy: https://support.google.com/analytics/answer/7318509?hl=en
- Google data use: https://policies.google.com/technologies/partner-sites?hl=en
- Google GA4 cookie configuration defaults: https://developers.google.com/analytics/devguides/collection/ga4/reference/config
- Google opt-out add-on: https://tools.google.com/dlpage/gaoptout

This audit implements verifiable website improvements; unresolved business facts above prevent a blanket compliance certification.

## Verification

- Build, SEO checks, all-five-language rollout preservation, legal/metadata/link checks, JS syntax checks and VM experiment tests passed.
- Browser checked policy at desktop and 320/390/768px frames; no horizontal overflow in the policy. Japanese and English render; English section navigation works. Japanese footer legal text remains above the fixed action bar and keyboard navigation reaches it.
- Isolated browser event capture verified one directions click and each Instagram destination (bar/chuck), with the original rollout IDs, B winner and active confidence-test variant. No synthetic clicks sent to production GA4. Phone/menu and both experiment variants covered by VM checks.
- No site JavaScript console errors observed; Chrome extension metadata errors are outside the site. No physical iPhone/Safari session was available; responsive checks used cloud Chrome.
- GA4 files and experiment configuration are unchanged byte-for-byte from v28; no GA4 administration settings, conversion names or historical data changed.
- Temporary QA fixtures removed before packaging.

## Follow-up — 24 October 2026

Owner confirmed the cover charge includes tax with no additional fee added after ¥500. Added explicit localized tax-inclusive wording to both cover-charge mentions in EN/JA/KO/TH/zh-Hans, including the app translation dictionary. Price, drink minimum, destinations, analytics and experiments unchanged.
