
## Quick orientation for AI agents

This repository is a single-file Streamlit app (`app.py`) that fetches public Sleeper fantasy league data, caches it, and displays standings/metrics. Edits should be small, functional, and UI-focused.

Key principles (why the repo is structured this way):
- Single entrypoint: `app.py` keeps UI, data fetching, and rendering together for simplicity—prefer minimal, local edits over sweeping refactors.
- Cache-first: `@st.cache_data(ttl=43200)` (12h) is used for API calls to limit rate and latency; respect the TTL unless you explicitly change cache behavior.

## Quick orientation for AI agents

This repo is a single-file Streamlit dashboard: `app.py`. The app fetches public Sleeper fantasy league data, caches it, and renders standings and weekly/season highlights. Keep edits focused, small, and UI-first — prefer adding helpers in `app.py` rather than wide refactors.

Key points to read first
- `LEAGUES` (top of `app.py`): mapping of human league name -> Sleeper league ID. The app warns if any ID looks like a placeholder (commonly prefixed with `YOUR_`).
- Cached fetchers: `fetch_league_info`, `fetch_rosters`, `fetch_users`, `fetch_matchups`, `fetch_nfl_state`. They use `requests.get` and are decorated with `@st.cache_data` (TTLs: 43200s for most league fetchers, 3600s for nfl state).
- Data normalization helpers: `_extract_entries_from_matchups`, `resolve_team_name_from_roster_id`, `get_team_name` — these implement defensive parsing of Sleeper payload shapes and name fallbacks (metadata.team_name -> display_name -> username -> Team {id}).
- UI renderers: `display_league_standings` builds a pandas DataFrame from `roster['settings']` and uses `components.html` for a custom table (falls back to `st.dataframe` on error). Weekly/season highlights use `st.columns` + inline HTML/CSS.

Data flow & integrations (concrete)
- Source: Sleeper REST API base `https://api.sleeper.app/v1/league/{league_id}` and subpaths `/rosters`, `/users`, `/matchups/{week}` and global `https://api.sleeper.app/v1/state/nfl`.
- `fetch_matchups(league_id, week=None)` probes week endpoints (1..18) when no week is supplied and normalizes results. Add similar fetchers using the same `requests` + `@st.cache_data` pattern.

Project conventions & gotchas
- Single entrypoint: keep runtime logic in `app.py`. Small, local edits are preferred.
- Caching: respect the existing TTLs. If adding network helpers, annotate with `@st.cache_data(ttl=43200)` unless you have a reason to pick a different TTL (document it).
- Defensive parsing: Sleeper payloads vary. Reuse `_extract_entries_from_matchups` style: tolerant checks, fallbacks, and explicit numeric defaults (e.g., settings.get('fpts', 0)).
- HTML embedding: custom table uses `components.html(...)` and a safe fallback to `st.dataframe` if embedding fails — follow that pattern when adding UI HTML.
- Timezone: page shows last-updated in America/New_York using `zoneinfo.ZoneInfo` — respect that for timestamps.

Developer workflows (reproducible)
- Install & run (Windows PowerShell):
  pip install -r requirements.txt
  streamlit run app.py
- Quick verify: edit a visible label or add a column in `display_league_standings`, save, and refresh the Streamlit UI.

Quality gates & validation
- Minimal smoke test: run the app locally and confirm the page loads and the changes appear in the UI.
- Keep `requirements.txt` changes documented and minimal.
- There are no unit tests in the repo — prefer small manual verifications. If you add tests, include them and update README.

Concrete examples to guide edits
- Add a cached endpoint: copy `fetch_rosters` style and annotate with `@st.cache_data(ttl=43200)`; return [] on empty results rather than None where convenient for downstream list-processing.
- Add a column to standings: modify the dict appended to `standings_data` in `display_league_standings` and include that key in the DataFrame column order (the table rendering expects explicit column ordering).
- Resolve team display: use `resolve_team_name_from_roster_id(roster_id, league_name, league_rosters, league_users)` to get consistent names for highlights and tables.

Files to inspect
- `app.py` — single source of truth for behavior and UI.
- `requirements.txt` — runtime deps (Streamlit, requests, pandas).
- `README.md`, `SETUP_GUIDE.md`, `update_data.yml` — docs and scheduled-update config.

Do / Don't (short)
- Do: keep edits local to `app.py`, preserve cache decorators & TTLs, prefer UI-friendly error messages (`st.error`, `st.warning`).
- Don't: introduce secret management, broad architectural refactors, or change deployment assumptions without documenting them in `README.md`.

If something is unclear or you'd like me to add an example edit (e.g., add a new cached endpoint, show how to add a standings column, or make a small UI tweak), say which area and I will update this file or create the code change.
