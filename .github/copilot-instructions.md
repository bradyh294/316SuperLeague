## Quick orientation for AI agents

This repo is a tiny Streamlit dashboard with a single entrypoint: `app.py`. It fetches public Sleeper fantasy-league data, caches it, and renders standings and highlights. Keep edits small, local, and UI-focused.

Why single-file: `app.py` intentionally contains UI, data fetchers, and renderers to keep the project simple and easy to run locally. Avoid large refactors — add small helper functions inside `app.py` when needed.

Key files & symbols to read first
- `app.py` — everything lives here. Read top-to-bottom: constants, cached fetchers, helpers, then UI renderers.
- `LEAGUES` — mapping of human-friendly names -> Sleeper league IDs (validate IDs for placeholders like `YOUR_...`).
- Cached fetchers: `fetch_league_info`, `fetch_rosters`, `fetch_users`, `fetch_matchups`, `fetch_nfl_state` (decorated with `@st.cache_data`).
- Normalizers/helpers: `_extract_entries_from_matchups`, `resolve_team_name_from_roster_id`, `get_team_name` — use these to keep naming consistent.
- UI renderer: `display_league_standings` builds the standings DataFrame and uses `components.html(...)` with a fallback to `st.dataframe`.

Concrete conventions and patterns
- Caching: league fetchers use `@st.cache_data(ttl=43200)` (12h); NFL state uses `ttl=3600` (1h). Preserve these TTLs unless you document a reason.
- Defensive parsing: Sleeper payloads vary. Follow `_extract_entries_from_matchups` for safe access and sensible defaults (e.g. use `.get(..., 0)` for numeric fields).
- API usage: endpoints follow `https://api.sleeper.app/v1/league/{league_id}` and subpaths `/rosters`, `/users`, `/matchups/{week}`; NFL state is `https://api.sleeper.app/v1/state/nfl`.
- HTML embedding: prefer `components.html` for rich tables but always keep a `st.dataframe` fallback.
- Timezone: timestamps use `zoneinfo.ZoneInfo('America/New_York')` — keep that for consistency in UI.

Developer workflow (Windows PowerShell)
- Install deps: `pip install -r requirements.txt`
- Run locally: `streamlit run app.py`
- Quick smoke: edit a visible string or add a column in `display_league_standings`, save, and refresh the Streamlit page.

Small, safe edits examples
- Add cached endpoint: copy the style of `fetch_rosters` and add `@st.cache_data(ttl=43200)`; return `[]` for empty lists (safer than `None`).
- Add standings column: append to the `standings_data` dict in `display_league_standings` and include the key in the DataFrame column order the renderer expects.

Notes & limitations
- No unit tests in repo; prefer manual checks in the running Streamlit UI. Keep changes minimal to avoid breaking the simple single-file flow.
- Avoid committing secrets or introducing external credential flows — the app queries public Sleeper endpoints.

If anything is unclear or you want me to add an example edit (new cached fetcher, extra standings column, or a small UI tweak), tell me which and I'll apply the change in `app.py`.
