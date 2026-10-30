# Autonomous optimization

The current entrypoint is `automation/weekly.py`; operating instructions are in `OPTIMIZER.md`.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r automation/requirements-lock.txt
.venv/bin/python automation/weekly.py
.venv/bin/python automation/experiments.py apply
```

Use Codex's weekly project task, model `gpt-6-luna`, reasoning `high`. No LLM API calls are made by Python. The scheduled model uses Sites to publish verified changes within the owner's standing authorization.

Credentials are read from `~/.config/fxxkup-seo/google-token.json` and `bigquery-token.json`, with optional FXXKUP_OAUTH_TOKEN_FILE and FXXKUP_BIGQUERY_TOKEN_FILE overrides. Both refresh in memory. Python writes only ignored `reports/` files during collection. The old three-job Hermes pipeline is retired.

Reports are immutable under `reports/runs/`; `latest.json` points to the last fully successful run. `last-attempt.json` also records failures. Raw cohort IDs never go to disk. Native GBP performance is explicitly unavailable unless a validated manual snapshot exists; automatic GBP-tagged GA4 website reports are separate.

Experiments use preregistered start/end/final-analysis times, a 24-hour conversion window, a three-full-day export settling delay, missing-table checks, QA/debug exclusions, crossover and assignment-ratio checks. A and B can win; insufficient power closes inconclusive. Weekly observations cannot stop a test for significance. Minimum baseline evidence and maximum enrollment duration gate new launches. Statistical significance does not establish actual bar visits or revenue.

Validation:
```sh
.venv/bin/python -m unittest discover -s tests/automation -v
node tests/experiment-rollout.cjs
.venv/bin/python scripts/check-seo.py
.venv/bin/python automation/validate_site.py
```
The former `tests/check-rollout.py` compares against a historical v26 snapshot and is archival, not the current deployment check.
