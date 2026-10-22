# Experiment release: permanent B winners and prepared confidence test

## Published baseline

Recovered published v26, commit `cb5c17e6758df33097b4795c8a4a2159457481d5`, on 22 October 2026. This release implements Chuck's decision to adopt B for both existing tests; it does not claim statistical significance.

- Directions winner: GET DIRECTIONS, with the existing station-walk supporting line, localized in all five languages.
- Footer winner: LET'S TALK and the existing visit/questions/bookings prompt, with separate official-bar and Chuck Instagram links, localized in all five languages.
- Winners are static HTML and work without JavaScript. Old stored A/B assignments are left intact but are never consulted. The old A content and randomization bootstraps have been removed.
- GA4 history and definitions are not deleted or changed. Retired test IDs no longer receive `experiment_view` or `experiment_id` traffic, preserving a clean historical experiment period.
- Action names remain `directions_click`, `instagram_click`, `phone_click`, `menu_open`, `find_us_click`, `google_reviews_click`, and `language_select`. Existing placement/language fields remain. Clicks retain destination and URL; rolled-out actions additionally carry `rollout_id` and `rollout_variant: B` rather than masquerading as randomized experiment observations.

## Confidence test — launch authorized 22 October 2026

Config: `source/experiments.json`, `firstVisit.enabled: true`.

ID: `first_visit_confidence_2026_10_v1`.

Key: `fxxkup_first_visit_confidence_2026_10_v1`.

The owner authorized launching this test on 22 October 2026. This release enables assignment, localized challenger copy, exposure events and click attribution. URL parameters cannot force an arm or change the launch setting. Setting enabled back to false pauses enrollment and attribution without deleting assignments or historical events.

### Hypothesis and arms

The hypothesis is that a clearer promise about music, whisky and a friendly welcome increases directions intent among visitors who see the hero.

- A: existing localized hero headline and supporting copy, unchanged.
- B English headline: **Your music. Your whisky. Your night.**
- B English supporting copy: **Song requests welcome. Great whisky, rock music, and a friendly place to spend your night in Susukino.**
- Japanese, Korean, Thai and Simplified Chinese challenger text is prepared in the same config. Japanese headings omit sentence-ending punctuation, consistent with the existing site.
- Both arms use exactly the same permanent B directions CTA, station-walk note, Maps URL, photos, layout and contact footer. Only the headline/supporting-copy pair changes.

### Enrollment and exposure when launched

This is a test of first-visit confidence, not a restriction to first-time GA4 users. All eligible human visitors can enroll in the enabled release.

- 50/50 random assignment stored in localStorage. The same assignment follows language-route navigation on the same origin and subsequent visits in that browser.
- As with the existing site's browser storage, www and apex origins have separate storage, and different browsers/devices are separate assignments. Use the site's canonical origin consistently.
- Visitors with unavailable persistent storage see the existing copy and are excluded from enrollment. Do not re-randomize them on each page.
- Exposure: `experiment_view`, once per document, after at least 25% of the hero-copy region is visible. A hero-link click also confirms exposure if the observer has not run or is unavailable. A visit landing below the hero does not count as exposed merely because a variant was assigned.
- Every post-exposure tracked action includes `experiment_id`, `experiment_variant`, `page_language`, `link_placement`, `link_url` and destination where applicable. Existing rollout markers remain independent of the new experiment.
- Page reloads and language changes can produce another document exposure, while the assignment stays the same. Use exposed users or properly joined sessions as denominators, not raw exposure-event count.

### Planned GA4 comparison

Use existing event-scoped dimensions `experiment_id` and `experiment_variant`; no new GA4 property or tag is required. First verify those dimensions remain registered.

Filter to `experiment_id = first_visit_confidence_2026_10_v1`, then compare A and B:

| Measure | Definition |
|---|---|
| Primary | Unique users with an attributed `directions_click` / unique exposed users |
| Supporting | Hero directions clicks; all-site directions clicks by placement |
| Secondary | Unique exposed users clicking Instagram, separated by `bar` / `chuck` destination |
| Diagnostic | Exposure split, page language, source/medium, device, menu clicks |

In Explore, establish exposed-user segments or a closed funnel from `experiment_view` to the desired action, and retain ID/variant filtering at both steps. Do not divide unrelated property-wide clicks by this experiment's exposures or compare event count with user count. Preserve acquisition context and break out locale only when counts support it.

Before launch, agree on the minimum detectable effect and required sample size from the new baseline. Run across complete weekly cycles, inspect assignment imbalance and exclude identified QA/internal activity. Do not choose a winner from a handful of clicks or repeated early peeks. Directions clicks measure intent, not confirmed arrivals or revenue.

### Release and reporting checklist

1. Review localized challenger renderings. GA4 report configuration must be verified separately if its UI is unavailable.
2. Compare complete weekly cycles; inspect assignment balance and QA/internal activity before interpreting results. Agree on a sample target before declaring a winner.
3. The approved release sets only `firstVisit.enabled` to true and rebuilds all locale pages.
4. Run regression checks and isolated browser checks for both arms. Do not add a public query-string force-variant switch.
5. Publish the enabled release and record its version/time. Distinguish local payload verification from confirmation in GA4 Realtime/DebugView. On this launch attempt the GA4 property UI returned request errors and remained loading, so a saved Explore report and GA4 ingestion confirmation remain pending; website enrollment does not depend on that UI.

Emergency pause: set `enabled` back to false, rebuild and publish. Leave assignment keys and historical GA4 events intact. Changing the challenger meaningfully should use a new ID and key.

## Checks

- `python3 scripts/check-seo.py`
- `python3 tests/check-rollout.py`
- `node tests/experiment-rollout.cjs`
- Browser inspection of the actual generated locale pages, plus isolated event capture where practical. Automated event assertions do not prove arrival in Google's reporting pipeline.
