import streamlit as st
import streamlit.components.v1 as components
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import html as _html

# Configure the page
st.set_page_config(
    page_title="316 Super League",
    page_icon="🏈",
    layout="wide"
)

# League configuration - YOU WILL EDIT THIS SECTION
LEAGUES = {
    "League I": "1264438284327587840",
    "League II": "1259988024255578112", 
    "League III": "1266580171679334401",
    "League IV": "1256735075073011712",
    "League V": "1256993935205609472"
}

# Cache data for 12 hours (43200 seconds)
@st.cache_data(ttl=43200)
def fetch_league_info(league_id):
    """Fetch basic league information"""
    try:
        response = requests.get(f"https://api.sleeper.app/v1/league/{league_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching league info: {e}")
        return None

@st.cache_data(ttl=43200)
def fetch_rosters(league_id):
    """Fetch rosters for a league"""
    try:
        response = requests.get(f"https://api.sleeper.app/v1/league/{league_id}/rosters")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching rosters: {e}")
        return None

@st.cache_data(ttl=43200)
def fetch_users(league_id):
    """Fetch users for a league"""
    try:
        response = requests.get(f"https://api.sleeper.app/v1/league/{league_id}/users")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        return None


@st.cache_data(ttl=43200)
def fetch_matchups(league_id, week=None):
    """Fetch matchups for a league.

    If `week` is provided, fetch /matchups/{week}. If not, probe weeks 1..18 and return a combined list of matchups found.
    Returns a list (possibly empty) or None on network error.
    """
    try:
        if week is not None:
            url = f"https://api.sleeper.app/v1/league/{league_id}/matchups/{week}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            return []

        # No specific week: probe common week range and collect results
        collected = []
        for w in range(1, 19):
            url = f"https://api.sleeper.app/v1/league/{league_id}/matchups/{w}"
            resp = requests.get(url, timeout=6)
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    # attach week if not present in items
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and 'week' not in item:
                                item['week'] = w
                        collected.extend(data)
                except Exception:
                    continue
        return collected
    except Exception as e:
        st.error(f"Error fetching matchups: {e}")
        return None


def _extract_entries_from_matchups(raw_matchups):
    """Normalize various matchup payload shapes into a flat list of entries.

    Each entry: {'league': league_name, 'week': int, 'matchup_id': str|int, 'roster_id': int, 'points': float}
    This function is defensive and attempts to extract common shapes returned by the Sleeper API.
    """
    entries = []
    if not raw_matchups:
        return entries

    for idx, m in enumerate(raw_matchups):
        # Week and matchup identifier if present
        week = m.get('week') if isinstance(m, dict) else None
        matchup_id = m.get('matchup_id') if isinstance(m, dict) else None

        # Case 1: a flat record that already contains roster_id & points
        if isinstance(m, dict) and 'roster_id' in m and 'points' in m:
            entries.append({'week': week, 'matchup_id': matchup_id or idx, 'roster_id': m.get('roster_id'), 'points': m.get('points')})
            continue

        # Case 2: m contains lists of participant dicts (common)
        if isinstance(m, dict):
            for v in m.values():
                if isinstance(v, list):
                    for item in v:
                        if isinstance(item, dict) and 'roster_id' in item and ('points' in item or 'points' in item):
                            entries.append({'week': week, 'matchup_id': matchup_id or idx, 'roster_id': item.get('roster_id'), 'points': item.get('points')})
        # Case 3: sometimes API returns a flat list of records (handle earlier in caller)
    return entries


@st.cache_data(ttl=3600)
def fetch_nfl_state():
    """Fetch NFL state from Sleeper (week, season, etc)."""
    try:
        resp = requests.get("https://api.sleeper.app/v1/state/nfl", timeout=6)
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception:
        return None


def find_latest_completed_week(all_entries, completeness_threshold=0.8):
    """Return the latest week (int) considered completed across all matchups.

    Criteria: for each week, group entries by (league, matchup_id). A matchup is complete if all entries for
    that matchup have a numeric non-null 'points'. A week is considered complete if the fraction of complete
    matchups >= completeness_threshold. Returns None if no week meets the threshold.
    """
    if not all_entries:
        return None

    # group entries by week -> by (league, matchup_id)
    weeks = {}
    for e in all_entries:
        w = e.get('week')
        if w is None:
            continue
        mid = e.get('matchup_id')
        league = e.get('league')
        key = f"{league}:{mid}"
        weeks.setdefault(w, {}).setdefault(key, []).append(e)

    candidate_weeks = []
    for w, matchups in weeks.items():
        total = len(matchups)
        if total == 0:
            continue
        complete = 0
        for grp in matchups.values():
            ok = True
            for ent in grp:
                pts = ent.get('points')
                if pts is None:
                    ok = False
                    break
            if ok:
                complete += 1
        frac = complete / total
        if frac >= completeness_threshold:
            candidate_weeks.append(w)

    if candidate_weeks:
        return max(candidate_weeks)

    # Fallback: pick the week with the highest fraction of complete matchups
    best_week = None
    best_frac = 0.0
    for w, matchups in weeks.items():
        total = len(matchups)
        if total == 0:
            continue
        complete = 0
        for grp in matchups.values():
            ok = True
            for ent in grp:
                if ent.get('points') is None:
                    ok = False
                    break
            if ok:
                complete += 1
        frac = complete / total
        if frac > best_frac:
            best_frac = frac
            best_week = w

    return best_week

def get_team_name(roster, users):
    """Get team name from roster and users data"""
    if not users:
        return f"Team {roster['roster_id']}"
    
    owner_id = roster['owner_id']
    for user in users:
        if user['user_id'] == owner_id:
            if user.get('metadata', {}).get('team_name'):
                return user['metadata']['team_name']
            elif user.get('display_name'):
                return user['display_name']
            else:
                return user.get('username', f"Team {roster['roster_id']}")
    
    return f"Team {roster['roster_id']}"


def resolve_team_name_from_roster_id(roster_id, league_name, league_rosters, league_users):
    """Resolve a human-friendly team name for a given roster_id using cached rosters and users.

    Returns a string team name or a fallback like 'Team {roster_id}'.
    """
    try:
        rosters = league_rosters.get(league_name, []) if league_rosters is not None else []
        users = league_users.get(league_name, []) if league_users is not None else []
    except Exception:
        rosters = []
        users = []

    for roster in rosters:
        try:
            if roster.get('roster_id') == roster_id:
                return get_team_name(roster, users)
        except Exception:
            continue

    return f"Team {roster_id}"

def display_league_standings(league_name, league_id, league_index=0, total_leagues=1):
    """Display standings for a single league"""
    st.subheader(f"🏆 {league_name}")
    
    # Check if league ID is set
    if league_id.startswith("YOUR_") or not league_id:
        st.warning(f"⚠️ Please update the league ID for {league_name} in the app.py file")
        return
    
    # Fetch data
    league_info = fetch_league_info(league_id)
    rosters = fetch_rosters(league_id)
    users = fetch_users(league_id)
    
    if not league_info or not rosters:
        st.error(f"❌ Could not load data for {league_name}")
        return
    
    # Create standings dataframe
    standings_data = []
    for roster in rosters:
        settings = roster.get('settings', {})
        team_name = get_team_name(roster, users)
        
        standings_data.append({
            'Team': team_name,
            'Wins': settings.get('wins', 0),
            'Losses': settings.get('losses', 0),
            'Ties': settings.get('ties', 0),
            'Points For': round(settings.get('fpts', 0), 1),
            'Points Against': round(settings.get('fpts_against', 0), 1)
        })
    
    # Sort by wins (descending), then by points for (descending)
    standings_data.sort(key=lambda x: (x['Wins'], x['Points For']), reverse=True)
    
    # Add rank
    for i, team in enumerate(standings_data):
        team['Rank'] = i + 1
    
    # Display as table
    df = pd.DataFrame(standings_data)
    df = df[['Rank', 'Team', 'Wins', 'Losses', 'Ties', 'Points For', 'Points Against']]

    # Highlight promotion/demotion rows:
    # - Top 3 are promotion spots (green) unless this is the top league (league_index == 0)
    # - Bottom 3 are demotion spots (red) unless this is the bottom league (league_index == total_leagues - 1)
    def _row_style(row):
        try:
            rank = int(row['Rank'])
        except Exception:
            return [''] * len(row)

        n = len(df)
        promotion_allowed = league_index != 0
        demotion_allowed = league_index != (total_leagues - 1)

        # Faded colors (low-key backgrounds)
        promo_color = 'background-color: #e6f4ea'  # soft green
        demo_color = 'background-color: #fdecea'   # soft red

        if promotion_allowed and rank <= 3:
            return [promo_color] * len(row)
        if demotion_allowed and rank > n - 3:
            return [demo_color] * len(row)
        return [''] * len(row)

    # Render a custom HTML table so we can control colors for light/dark mode.
    # Build classes for each row (promo/demo/none) then render HTML with a small CSS block
    n = len(df)
    promotion_allowed = league_index != 0
    demotion_allowed = league_index != (total_leagues - 1)

    # Build table header
    headers = list(df.columns)

    import html as _html

    rows_html = ""
    for _, row in df.iterrows():
        try:
            rank = int(row['Rank'])
        except Exception:
            rank = None

        cls = ""
        if promotion_allowed and rank is not None and rank <= 3:
            cls = "promo"
        elif demotion_allowed and rank is not None and rank > n - 3:
            cls = "demo"

        # Escape cell contents to avoid breaking the HTML if team names contain <, &, etc.
        row_cells = "".join(f"<td>{_html.escape(str(row[h]))}</td>" for h in headers)
        rows_html += f"<tr class=\"{cls}\">{row_cells}</tr>\n"
    # CSS uses prefers-color-scheme to pick subtle backgrounds that read well in both themes.
    css = '''
    <style>
    .sl-table { border-collapse: collapse; width: 100%; background: transparent; }
    .sl-table th, .sl-table td { padding: 8px 10px; text-align: left; border-bottom: 1px solid rgba(0,0,0,0.06); color: inherit; }
    .sl-table thead th { font-weight: 600; }
    /* Light mode faded colors */
    .promo { background-color: #e6f4ea; }
    .demo  { background-color: #fdecea; }
    /* Dark mode adjustments: set light text color and subtle translucent backgrounds */
    @media (prefers-color-scheme: dark) {
        .sl-table { background: transparent; }
        .sl-table th, .sl-table td { border-bottom: 1px solid rgba(255,255,255,0.06); color: #e6eef6; }
        .promo { background-color: rgba(38,166,91,0.12); }
        .demo  { background-color: rgba(239,83,80,0.12); }
    }
    </style>
    '''

    header_html = "".join(f"<th>{_html.escape(str(h))}</th>" for h in headers)
    html = f"""
    {css}
    <div class="sl-table-wrapper">
      <table class="sl-table">
        <thead><tr>{header_html}</tr></thead>
        <tbody>
        {rows_html}
        </tbody>
      </table>
    </div>
    """

    # Compute a reasonable height for the embedded HTML table and render via components.html
    try:
        row_height = 36
        padding = 60
        table_height = int(n * row_height + padding)
        max_height = 1200
        table_height = min(table_height, max_height)
    except Exception:
        table_height = 400

    # Try to embed the custom HTML. If embedding fails (e.g. security, rendering error), fall back to st.dataframe
    try:
        components.html(html, height=table_height, scrolling=True)
    except Exception as e:
        st.error(f"Could not render custom table HTML, falling back to Streamlit table: {e}")
        st.dataframe(df)
    
    # (Removed: per-request, metrics for Current Week / Regular Season Weeks / Total Teams)

# Main app
def main():
    st.title("🏈 316 Super League")
    # Display last-updated time in US Eastern Time
    try:
        now_et = datetime.now(tz=ZoneInfo("America/New_York"))
    except Exception:
        now_et = datetime.now()
    st.markdown(f"*Last updated: {now_et.strftime('%B %d, %Y at %I:%M %p %Z')}*")
    
    # Instructions for setup
    if any(league_id.startswith("YOUR_") for league_id in LEAGUES.values()):
        st.error("🔧 **Setup Required:** Please update your league IDs in the app.py file")
        st.markdown("""
        **To set up your dashboard:**
        1. Open `app.py` in a text editor
        2. Replace each `YOUR_LEAGUE_ID_HERE` with your actual Sleeper league ID
        3. You can find your league ID in the URL when viewing your league on Sleeper
        4. Save the file and refresh this page
        """)
        st.divider()
    

    # Collect rosters/users (cached) for all leagues once (needed by weekly highlights)
    league_rosters = {}
    league_users = {}
    for league_name, league_id in LEAGUES.items():
        league_rosters[league_name] = fetch_rosters(league_id) or []
        league_users[league_name] = fetch_users(league_id) or []

    # Weekly highlights (across all leagues) - moved to top so users see highlights first
    st.markdown("---")
    st.header("Weekly highlights")

    # Try to determine the latest completed week using the NFL state endpoint (fast)
    state = None
    try:
        state = fetch_nfl_state()
    except Exception:
        state = None

    if not state or 'week' not in state:
        st.info("Could not determine current NFL week from Sleeper; weekly highlights may be limited.")

    # Candidate weeks: start at reported NFL week and step back up to 4 weeks
    candidate_weeks = []
    if state and isinstance(state.get('week'), int):
        current_week = state.get('week')
        # start from the previous week (most recently completed week), not the current in-progress week
        start_week = max(current_week - 1, 1)
        for w in range(start_week, max(start_week - 4, 0), -1):
            candidate_weeks.append(w)
    else:
        # Fallback: try recent weeks 18..1 (but keep short to avoid probing too many)
        candidate_weeks = list(range(18, 14, -1))

    completeness_threshold = 0.8
    selected_week = None
    flat_entries = []

    # Collect entries per candidate week so we can pick a sensible fallback if no week meets the threshold
    week_to_entries = {}

    for w in candidate_weeks:
        week_entries = []
        total_matchups = 0
        complete_matchups = 0
        # Fetch matchups for this week across leagues (fast: single-week endpoints)
        for league_name, league_id in LEAGUES.items():
            raw = fetch_matchups(league_id, week=w) or []
            entries = _extract_entries_from_matchups(raw)
            # Add league name and collect; also resolve team names from roster_id
            for e in entries:
                e_copy = dict(e)
                e_copy['league'] = league_name
                # Resolve team display name if possible
                roster_id = e_copy.get('roster_id')
                if roster_id is not None:
                    e_copy['team'] = resolve_team_name_from_roster_id(roster_id, league_name, league_rosters, league_users)
                week_entries.append(e_copy)

            # compute matchup completeness per league
            # group by matchup_id
            mids = {}
            for e in entries:
                mid = e.get('matchup_id')
                if mid is None:
                    continue
                mids.setdefault(mid, []).append(e)
            for grp in mids.values():
                total_matchups += 1
                if all((ent.get('points') is not None) for ent in grp):
                    complete_matchups += 1

        week_to_entries[w] = week_entries

        frac = (complete_matchups / total_matchups) if total_matchups > 0 else 0.0
        if frac >= completeness_threshold:
            selected_week = w
            flat_entries = week_entries
            break

    # If none of the candidate weeks met threshold, fall back to the most recent candidate week that has any data
    if selected_week is None:
        non_empty_weeks = [w for w, entries in week_to_entries.items() if entries]
        if non_empty_weeks:
            # pick the most recent week (highest number) among those with data
            selected_week = max(non_empty_weeks)
            flat_entries = week_to_entries[selected_week]
            st.caption(f"Showing most recent week with data (may be in-progress): {selected_week}")
        else:
            st.info("No matchup data available for recent weeks to compute weekly highlights.")
            flat_entries = []

    # Render weekly highlights (always visible if data exists)
    if flat_entries:
        df_all = pd.DataFrame(flat_entries)

        # Subtitle showing the selected week
        if selected_week is not None:
            st.subheader(f"Week {selected_week}")

        # Highest scoring team
        try:
            top = df_all.loc[df_all['points'].idxmax()]
        except Exception:
            top = None
        # Lowest scoring team
        try:
            bottom = df_all.loc[df_all['points'].idxmin()]
        except Exception:
            bottom = None

        # Closest matchup: find pairs with same matchup_id and minimal abs diff
        closest = None
        # group by matchup_id
        for mid, group in df_all.groupby('matchup_id'):
            if len(group) < 2:
                continue
            pts = group['points'].tolist()
            if len(pts) >= 2:
                # compute min diff across pairs
                pts_sorted = sorted(pts)
                min_diff = min(abs(a - b) for a, b in zip(pts_sorted, pts_sorted[1:]))
                if closest is None or min_diff < closest['diff']:
                    # store the pair with min diff
                    closest = {'matchup_id': mid, 'diff': min_diff, 'group': group}

        col1, col2, col3 = st.columns(3)
        # Defensive getters and display preparation
        if top is not None:
            top_team = top.get('team', None) if hasattr(top, 'get') else (top['team'] if 'team' in top else None)
            top_league = top.get('league', '') if hasattr(top, 'get') else top.get('league', '')
            top_points = top.get('points', 0.0) if hasattr(top, 'get') else top.get('points', 0.0)
        else:
            top_team = None
            top_league = ''
            top_points = 0.0

        if bottom is not None:
            bottom_team = bottom.get('team', None) if hasattr(bottom, 'get') else (bottom['team'] if 'team' in bottom else None)
            bottom_league = bottom.get('league', '') if hasattr(bottom, 'get') else bottom.get('league', '')
            bottom_points = bottom.get('points', 0.0) if hasattr(bottom, 'get') else bottom.get('points', 0.0)
        else:
            bottom_team = None
            bottom_league = ''
            bottom_points = 0.0

        # Prepare closest matchup display
        closest_display = None
        if closest is not None:
            grp = closest['group']
            teams = []
            for _, r in grp.iterrows():
                t = r.get('team', None) if hasattr(r, 'get') else (r['team'] if 'team' in r else None)
                pts = r.get('points', 0.0) if hasattr(r, 'get') else r.get('points', 0.0)
                teams.append({'team': t or f"Team {r.get('roster_id', '?')}", 'points': float(pts)})
            if len(teams) >= 2:
                closest_display = (teams[0]['team'], teams[1]['team'], closest['diff'])

        # Render each highlighted box with larger subheading and league on its own line
        with col1:
            display_top = top_team or (f"Team {int(top.get('roster_id'))}" if top is not None and top.get('roster_id') is not None else "Team ?")
            html_top = f"""
            <div style='font-size:18px;font-weight:700;margin-bottom:6px;'>Highest scoring team</div>
            <div style='font-size:20px;font-weight:600;color:var(--sl-primary, #000000)'>{_html.escape(str(display_top))}</div>
            <div style='font-size:13px;color:var(--sl-muted, #6c757d)'>{_html.escape(str(top_league))}</div>
            <div style='font-size:20px;margin-top:6px;color:var(--sl-success, #1e7e34);font-weight:600'>{float(top_points):.2f} pts</div>
            """
            st.markdown(html_top, unsafe_allow_html=True)

        with col2:
            display_bottom = bottom_team or (f"Team {int(bottom.get('roster_id'))}" if bottom is not None and bottom.get('roster_id') is not None else "Team ?")
            html_bottom = f"""
            <div style='font-size:18px;font-weight:700;margin-bottom:6px;'>Lowest scoring team</div>
            <div style='font-size:20px;font-weight:600;color:var(--sl-primary, #000000)'>{_html.escape(str(display_bottom))}</div>
            <div style='font-size:13px;color:var(--sl-muted, #6c757d)'>{_html.escape(str(bottom_league))}</div>
            <div style='font-size:20px;margin-top:6px;color:var(--sl-danger, #e53935);font-weight:600'>{float(bottom_points):.2f} pts</div>
            """
            st.markdown(html_bottom, unsafe_allow_html=True)

        with col3:
            if closest_display is not None:
                t1, t2, diff = closest_display
                html_closest = f"""
                <div style='font-size:18px;font-weight:700;margin-bottom:6px;'>Closest matchup</div>
                <div style='font-size:20px;font-weight:600;color:var(--sl-primary, #000000)'>{_html.escape(str(t1))}</div>
                <div style='font-size:13px;color:var(--sl-muted, #6c757d)'>vs</div>
                <div style='font-size:20px;font-weight:600;color:var(--sl-primary, #000000)'>{_html.escape(str(t2))}</div>
                <div style='font-size:20px;margin-top:6px;color:var(--sl-primary, #000000);font-weight:600'>Δ {float(diff):.2f} pts</div>
                """
                st.markdown(html_closest, unsafe_allow_html=True)
            else:
                html_closest = f"""
                <div style='font-size:18px;font-weight:700;margin-bottom:6px;'>Closest matchup</div>
                <div style='font-size:14px;color:var(--sl-muted, #6c757d)'>No close matchups found</div>
                """
                st.markdown(html_closest, unsafe_allow_html=True)

        st.divider()

    # Display all leagues (first entry in LEAGUES is the top league)
    for idx, (league_name, league_id) in enumerate(LEAGUES.items()):
        display_league_standings(league_name, league_id, league_index=idx, total_leagues=len(LEAGUES))
        st.divider()

    # Footer
    st.markdown("---")
    st.markdown("💡 **Tip:** Data updates automatically every 12 hours.")
    st.markdown("📊 Built with Streamlit • Data from Sleeper API")

if __name__ == "__main__":
    main()
