
## Quick orientation for AI agents

This repository is a single-file Streamlit app (`app.py`) that fetches public Sleeper fantasy league data, caches it, and displays standings/metrics. Edits should be small, functional, and UI-focused.

Key principles (why the repo is structured this way):
- Single entrypoint: `app.py` keeps UI, data fetching, and rendering together for simplicity—prefer minimal, local edits over sweeping refactors.
- Cache-first: `@st.cache_data(ttl=43200)` (12h) is used for API calls to limit rate and latency; respect the TTL unless you explicitly change cache behavior.

What to look at first
- `app.py` — the entire app lives here. Important symbols:
  - `LEAGUES` dict (human name -> league ID). Placeholder IDs start with `YOUR_` and are checked at runtime.
  - `fetch_league_info`, `fetch_rosters`, `fetch_users` (all annotated with `@st.cache_data(ttl=43200)`).
  - `get_team_name(roster, users)` — fallback order: `user.metadata.team_name`, `display_name`, then `username`.
  - `display_league_standings(league_name, league_id)` — constructs a pandas DataFrame from roster `settings` and renders with Streamlit (`st.dataframe`, `st.metric`).

Data flow and integrations
- Source: Sleeper API endpoints under `https://api.sleeper.app/v1/league/{league_id}` and subpaths (`/rosters`, `/users`). Implement new fetchers following existing `requests.get` + `@st.cache_data` pattern.
- No secrets: league IDs are treated as non-secret and stored directly in `app.py`. The app does not read env vars or secret stores.

Developer workflows (commands you’ll actually run)
- Install deps and run locally (Windows PowerShell):
  ```powershell
  pip install -r requirements.txt
  streamlit run app.py
  ```
- Quick verification: update a visible label or add a column and refresh the Streamlit page to confirm changes.

Project conventions and patterns
- Keep edits small and localized to `app.py`. Add helper functions in the same file when appropriate.
- Use Streamlit caching decorators exactly as-is (`@st.cache_data(ttl=43200)`) for any network-bound helpers.
- UI-first error handling: use `st.error` / `st.warning` with clear, actionable text (e.g., "Update LEAGUES in app.py — found placeholder ID").
- Data shaping: roster metrics come from `roster['settings']` (fields like `wins`, `losses`, `fpts`, `fpts_against`). Ensure numeric defaults to avoid None values in pandas.

Quick examples
- Add a cached endpoint: replicate `fetch_rosters` pattern and annotate with `@st.cache_data(ttl=43200)`.
- Add a new column to standings: extend the dict appended to `standings_data` inside `display_league_standings` and include the key in DataFrame column order.

Quality gates & review checklist
- Keep changes backward-compatible and minimal. Run the app locally and confirm page loads and the modified UI element displays correctly.
- Update `requirements.txt` only when required; document why in PR.
- In PR description include: what changed, how to run locally, and one screenshot or expected visible effect.

Files to inspect when making changes
- `app.py` — main app and the only runtime source file.
- `requirements.txt` — list of runtime dependencies (Streamlit, requests, pandas).
- `README.md`, `SETUP_GUIDE.md`, `update_data.yml` — docs and scheduled-update configuration used by maintainers.

Do / Don't summary
- Do: make small, well-scoped edits in `app.py`, preserve cache decorators, use UI error messages, and run a local Streamlit smoke test.
- Don't: introduce secret management, perform broad refactors across multiple files, or change deployment expectations without documenting them in `README.md`.

If anything here is unclear or you'd like samples for a specific change (add column, new cached endpoint, UI tweak), tell me which area and I will iterate.

If anything above is unclear or you want more detail (for example, a proposed code change or a suggested test), tell me which area to expand and I will iterate.
