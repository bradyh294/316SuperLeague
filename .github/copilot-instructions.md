## Quick orientation for AI agents

This repo is a small Streamlit app (single-file app: `app.py`) that displays standings for five Sleeper fantasy leagues. The app retrieves public league data from the Sleeper API, caches it, and renders tables/metrics with Streamlit.

Goal: help an agent make safe, minimal edits (bugfixes, UI tweaks, new small features) without changing deployment expectations.

### Big picture
- `app.py` is the single entrypoint. It defines:
  - `LEAGUES` dict at top: map of human-readable league names to Sleeper league IDs. These are plain strings and the code explicitly checks for placeholders that start with "YOUR_".
  - Several `fetch_*` helpers annotated with `@st.cache_data(ttl=43200)` (12 hours): `fetch_league_info`, `fetch_rosters`, `fetch_users`.
  - `get_team_name(roster, users)` resolves a roster's display name using `user.metadata.team_name`, `display_name`, then `username`.
  - `display_league_standings(league_name, league_id)` builds a dataframe and renders it via Streamlit (`st.dataframe`, `st.metric`, columns layout).

### Data flow and integrations
- Source: Sleeper API via requests.get to `https://api.sleeper.app/v1/league/{league_id}` and subpaths (`/rosters`, `/users`). See `fetch_*` functions in `app.py`.
- Caching: Streamlit cache is used with TTL=43200s. Agents should respect or intentionally change the TTL only when necessary.
- No secret storage: league IDs are set in `app.py` and treated as non-secret (they must be public league IDs). The app does not read environment variables or secrets.

### Key development workflows
- Local run: install runtime from `requirements.txt` and run Streamlit.

  Example (Windows PowerShell):
  ```powershell
  pip install -r requirements.txt
  streamlit run app.py
  ```

- Deployment: recommended on Streamlit Community Cloud (README.md contains steps). Keep `requirements.txt` in repo root.
- Forcing updates: UI users can press Streamlit refresh; programmatic TTL changes are in `@st.cache_data(ttl=43200)`.

### Project-specific conventions and patterns
- Single-file app: add small features inside `app.py` following existing function structure. Prefer small, localized edits.
- UI-first error handling: code uses `st.error` / `st.warning` for user-facing errors. Keep messages human-readable and include actionable hints (e.g., "update LEAGUES in app.py").
- League ID placeholders: code checks for league IDs starting with `YOUR_` and shows a setup error; preserve that pattern for checks.
- Data shaping: standings are built from each roster's `settings` dict (keys like `wins`, `losses`, `fpts`, `fpts_against`) — tests/changes must keep numeric defaults to avoid None.

### Files to inspect when making changes
- `app.py` — main app; add functions here and follow existing caching and error-reporting patterns.
- `requirements.txt` — runtime deps (streamlit, requests, pandas). Keep versions conservative when adding deps.
- `README.md` — contains README and deploy notes; update when changing user-visible setup steps.
- `SETUP_GUIDE.md` / `update_data.yml` — auxiliary files referenced by README; inspect before changing scheduled-update behavior.

### Small actionable examples for common tasks
- Add a new cached endpoint: copy `fetch_rosters` pattern and use `@st.cache_data(ttl=43200)`.
- Show additional column in standings: modify the `standings_data.append` block in `display_league_standings` and include it in the DataFrame column ordering.
- Fix missing team name: `get_team_name` prefers `user.metadata.team_name` → `display_name` → `username`. If adding fallback logic, preserve this order.

### Safety and PR guidance
- Keep changes minimal and isolated in `app.py` (no large refactors in a single PR).
- Update `requirements.txt` only when necessary; prefer patch releases (e.g., `requests>=2.31.0`) and list added packages with rationale in PR body.
- Include a short smoketest in PR description: how to run locally and what visible change to expect (e.g., new column appears in table).

### What not to do
- Don't assume a complex multi-service architecture — the project is a single-process Streamlit app.
- Don't add environment-secret handling unless explicitly requested; league IDs are stored in code.

If anything above is unclear or you want more detail (for example, a proposed code change or a suggested test), tell me which area to expand and I will iterate.
