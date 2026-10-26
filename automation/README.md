# Rock Bar FxxK Up SEO + conversion pilot

Implemented inside the existing Sites source checkout, based on commit `49e79b4a15db4b9bf3507640e64b81057303cc54` (published version 30). Production is buildless HTML/JavaScript, not React. No competing site or second experiment runtime has been added. The pilot reuses `source/experiments.json`, `dist/experiments.js`, `dist/analytics.js` and the existing rollout tests. Source and deployed pages are unchanged.

## Run

Python 3.12 and Node 18+:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r automation/requirements-lock.txt
.venv/bin/python -m unittest discover -s tests/automation -v
.venv/bin/python automation/pilot.py --output reports
.venv/bin/python automation/pilot.py --live --output reports
```

Offline mode checks checked-out HTML, consumes no network and produces `weekly.md` and `evidence.json`. Live mode GETs four public pages plus robots and sitemap, and uses Google read-only APIs when Application Default Credentials are configured. It does not execute site JavaScript or emit GA4 events, Google searches, clicks, reviews or links. A three-day delay avoids recent partial data; GSC uses PT dates, GA4 uses the property's reporting timezone. Do not directly equate them. Requests have timeouts and a small fixed public-page budget. Certificate verification stays on; certifi resolves the local Python certificate-store issue found during validation.

The API collector retrieves separate GSC property totals for two 28-day periods, query/page/country/device rows (paginated, capped at 100k), and GA4 Organic Search sessions/engagement/key events by browser language. API top-row/privacy limits remain even after pagination. Metadata is retained for thresholding, sampling and truncation review. GA4 baseline is deliberately not treated as a visitor-level A/B cohort. The report includes dated browser observations separately from live data, and flags access gaps. Empty/missing data never becomes a claim of zero demand.

## Access verified on 27 October 2026 (Japan)

- Sites owner access: current source retrieved successfully; no save or deployment called.
- Authenticated browser read access to GSC domain `rockbarfxxkup.com` and GA4 property `559070143`.
- Live measurement ID: `G-JPYT9JRWBT`.
- Registered event dimensions: `experiment_id`, `experiment_variant`, `link_destination`. No registered `page_language`/`link_placement` dimensions were shown.
- Recent GA4 event receipt includes `experiment_view`, `directions_click`, `instagram_click`, `menu_open`, `language_select`. `directions_click` is a key event. This verifies historical receipt, not the pilot's synthetic test events.
- No Google Application Default Credentials available. The validated live run reports `DefaultCredentialsError` rather than inventing API data.
- No Business Profile admin data read. Website NAP/schema/maps are auditable; actual local-pack rankings, listing consistency and profile performance remain unverified.
- The authoritative source and write target are the existing Rock Bar FxxK Up Sites project. No separate GitHub repository is needed. The connected GitHub account has no matching writable bar repository.

## Scheduling activation (not yet active)

The source belongs to the existing Sites project, not GitHub. A GitHub Actions definition would not run from that project and is intentionally not included. The Sites schedule connector can create a recurring cloud task, but a schedule alone does not grant Google Analytics or Search Console API access, nor can it run this checked-in Python script as a shell job. Do not schedule a task that would be unable to read real data.

To activate unattended weekly reporting in this Sites setup:

1. Choose an approved read-only Google API identity: GA4 Viewer on property `559070143`, plus Search Console read access to `sc-domain:rockbarfxxkup.com`. Enable Analytics Data API and Search Console API in its Google Cloud project.
2. Provide that identity through a supported Sites runtime secret or authenticated data connection. Do not put credentials in source, task prompts, or report files. Verify the hosted task can retrieve both API datasets independently.
3. Adapt the Python collector to a supported hosted execution path (or move only the report runner to an approved scheduler). Preserve this Site as the source of truth. The current Sites schedule tool can schedule a cloud task, but does not execute the Python script itself.
4. Run one manual hosted dry run and inspect dates, API coverage, privacy limits, and report access. Then schedule Monday 08:00 Japan with the Sites schedule tool or the approved runner. Keep output private and read-only.
5. For experiment analysis, separately verify an authorized mature visitor-level export and pre-register the next test. Do not enable winner promotion, automatic merge, or deployment.

The live browser session already confirms human read access; it does not provide unattended credentials. The first scheduled report remains blocked on supported API access and runner setup. Sites owner access is verified; no scheduled task has been created.

## Existing A/B workflow and safeguards

- Directions/footer B are owner-selected permanent rollouts, not statistically established winners. Old storage keys and conversion names are preserved. See `experiment-history.json`.
- Active test `first_visit_confidence_2026_10_v1` already assigns 50/50 through persistent localStorage, holds assignment across language routes and falls back to unenrolled original content when storage is blocked. It measures exposure at 25% hero visibility or a hero CTA interaction. Exposure is deduplicated per page, not globally per visitor.
- Click events attach experiment ID/variant only after exposure. `directions_click` is the primary proxy; a click does not prove a visit. Instagram bar vs personal destinations remain separate.
- Python deduplicates exposures and conversions by pseudonymous visitor, excludes explicit QA rows, detects crossovers and sample-ratio mismatch, applies a 24-hour conversion window, and reports conversion rates, absolute/relative lift and conservative Wilson-based uncertainty. Events before exposure and after the window do not count.
- `--events /secure/path/cohort.jsonl` accepts authorized exported events with `visitor_id`, `experiment_id`, `variant`, `event`, `timestamp` (ISO 8601 with timezone), optional `qa`. This is an offline analysis input, never a tracking endpoint. Use the same pseudonymous identity across routes; never emails, IPs or phone numbers. Keep raw export local, excluded by `.gitignore`. Do not upload raw visitor rows to report artifacts.
- Export must include complete exposures, primary conversions and mature follow-up. Resolve late arrivals, mixed assignments, missing IDs, staff/testing/internal traffic, consent effects and repeated devices before inference. Do not build denominators by summing event counts or GA4 distinct users across event rows. A raw BigQuery extraction adapter is not implemented yet.
- Existing test has no verified prospective power plan, so `preregistered=false`; no winner can be declared from this pilot. The sample value is a planning example, not a validated requirement for this site. Do not change it retrospectively to force a result. For the next version, predefine baseline, MDE, allocation, enrollment dates, sample, final analysis date and mature conversion cutoff. The conservative decision interval needs its own power simulation before adoption.
- Minimum duration, sample target, mature window, prospective registration and human guardrail review all gate recommendations. Weekly reports are descriptive; do not repeatedly peek for significance. “recommend_B_for_review” is still only a recommendation; no change is applied. Null results remain insufficient evidence.
- Guardrails to review: technical errors, broken navigation, menu/Instagram/phone engagement, mobile usability, language balance, assignment persistence, same-URL SEO behavior. Current boolean review is a deliberate human gate; automated guardrail collection is not implemented.
- SEO ranking hypotheses are separate: use a dated change log and observational pre/post comparisons with seasonality/channel caveats. Visitor randomization does not estimate ranking impact. No user-agent cloaking or separate search-engine content.

## First recommendations, tied to observed evidence

1. Japanese local-intent snippet review: `札幌 ロックバー` had 11 impressions/0 clicks and displayed position 1; `すすきの ロックバー` 9/0 at position 1. Verify intent and title/snippet usefulness, then collect more data. These counts do not justify a ranking fix. Avoid implying record/vinyl-bar offerings merely because `札幌 レコードバー` appeared.
2. English: 156 browser-language active users, but acquisition mixes direct/social/search and may include testing. The existing welcoming hero hypothesis is appropriate to measure; no conversion advantage is proven.
3. Korean: two browser-language users and no query evidence in the ten visible GSC rows. Thai: no row in the language report. Preserve the existing translated pages; do not mass-generate content. Candidate research themes are accurate directions, sixth-floor access and verified bar details; validate with actual queries/local feedback before proposing copy.
4. Site baseline: four language pages returned 200 and passed implemented canonical, language, title, description, H1, hreflang, robots-meta, schema-presence and social/maps-link checks. These are static checks, not rich-results validation, Core Web Vitals or proof of indexation. Robots/sitemap bodies are retained for review; Search Console indexing must be checked separately.
5. Local visibility: manually compare official listing name/address/phone/hours with website schema and Maps destination. Do not alter listing information without verification; do not create reviews or links.

## Tests and limits

14 Python tests plus the existing JavaScript runtime suite passed. Tests cover deduplication, pre-exposure and late conversions, insufficient evidence gates, imbalance, crossovers, null outcomes, multilingual routing and an end-to-end bridge from actual mocked browser runtime events to the Python analyzer. Synthetic events stay inside tests and are never sent to Google. HTTP/API calls are mocked in unit tests; live public reads were separately verified. Real authenticated Google API reads and visitor-cohort analysis remain blocked by access/export setup.

Sources: [GSC query API](https://developers.google.com/webmaster-tools/v1/searchanalytics/query), [GA4 runReport](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport), [Google website experiment precautions](https://developers.google.com/search/docs/crawling-indexing/website-testing). These informed endpoint structure and separation of ranking from conversion experiments.
