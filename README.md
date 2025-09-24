# 316 Super League Dashboard

A free, web-based fantasy football dashboard for your Premier League-style league system with promotion and relegation. Built with Streamlit and deployed on Streamlit Community Cloud at zero cost.

## 🚀 Quick Start

### 1. Get Your League IDs
1. Go to your Sleeper league page in a web browser
2. Look at the URL - it will be something like `https://sleeper.app/leagues/123456789/team`
3. The number (`123456789`) is your league ID
4. Repeat for all 5 leagues

### 2. Configure Your Leagues
Edit `app.py` and replace the placeholder league IDs:

```python
LEAGUES = {
    "Premier League": "YOUR_ACTUAL_LEAGUE_ID_HERE",
    "Championship": "YOUR_ACTUAL_LEAGUE_ID_HERE", 
    "League I": "YOUR_ACTUAL_LEAGUE_ID_HERE",
    "League II": "YOUR_ACTUAL_LEAGUE_ID_HERE",
    "National League": "YOUR_ACTUAL_LEAGUE_ID_HERE"
}
```

### 3. Test Locally (Optional)
```bash
pip install -r requirements.txt
streamlit run app.py
```

### 4. Deploy to Streamlit Community Cloud
1. Push your code to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Deploy your app by selecting the repository and `app.py`
5. Your dashboard will be live at `https://yourapp.streamlit.app`

## 📊 Features

- **Real-time standings** for all 5 leagues
- **Team records** with wins, losses, and points
- **Automatic data caching** (updates every 12 hours)
- **Mobile-responsive** design
- **Zero hosting costs** with Streamlit Community Cloud

## 🔧 Customization

### Change League Names
Update the `LEAGUES` dictionary in `app.py`:
```python
LEAGUES = {
    "Your Custom Name 1": "league_id_1",
    "Your Custom Name 2": "league_id_2",
    # ... etc
}
```

### Add More Data
The Sleeper API provides tons of data. You can extend the dashboard with:
- Weekly matchups
- Player statistics  
- Waiver wire activity
- Trade history
- And much more!

## 🔄 Data Updates

The dashboard automatically caches data for 12 hours. To force an update:
1. Click the refresh button in Streamlit (top-right corner)
2. Or wait for the automatic refresh

For more frequent updates, you can:
1. Reduce the `ttl` value in the `@st.cache_data` decorators
2. Set up the GitHub Actions workflow for scheduled updates

## 📱 Sharing Your Dashboard

Once deployed, you can share your dashboard URL with all league members. The dashboard is:
- ✅ **Public** - anyone with the URL can view it
- ✅ **Fast** - cached data loads instantly  
- ✅ **Free** - no hosting costs ever
- ✅ **Reliable** - hosted on Streamlit's infrastructure

## 🆘 Troubleshooting

### "Could not load data" error
- Check that your league IDs are correct
- Make sure your leagues are public (not private)
- Verify you're using the current season's league IDs

### App won't deploy
- Check that `requirements.txt` is in the repository root
- Ensure your GitHub repository is public
- Verify `app.py` is in the repository root

### Data seems outdated
- Remember data caches for 12 hours by default
- Use the Streamlit refresh button to force updates
- Check if there were any API issues with Sleeper

## 🚀 Next Steps

Want to enhance your dashboard? Consider adding:

1. **Weekly matchup display**
2. **Cross-league leaderboards** 
3. **Playoff bracket visualization**
4. **Team performance charts**
5. **Player pickup/drop tracking**

## 📞 Support

- Sleeper API Documentation: [docs.sleeper.com](https://docs.sleeper.com)
- Streamlit Documentation: [docs.streamlit.io](https://docs.streamlit.io)
- Need help? Check the GitHub issues or create a new one

---

**Built for the 316 Super League** ⚽ | Powered by Sleeper API & Streamlit
