import streamlit as st
import streamlit.components.v1 as components
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd

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
    "League IV": "1183903923345235968",
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

        row_cells = "".join(f"<td>{row[h]}</td>" for h in headers)
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

    header_html = "".join(f"<th>{h}</th>" for h in headers)
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

    components.html(html, height=table_height, scrolling=True)
    
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
