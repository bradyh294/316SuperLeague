# 316 Super League Configuration Guide

## Step 1: Find Your League IDs

For each of your 5 leagues, follow these steps:

1. Go to Sleeper.app and navigate to your league
2. Look at the URL in your browser - it will look like:
   `https://sleeper.app/leagues/987654321/team`
3. The number in the URL (987654321) is your League ID
4. Copy this number

## Step 2: Update Your League Configuration

Open `app.py` and find this section (around line 11):

```python
LEAGUES = {
    "Premier League": "YOUR_PREMIER_LEAGUE_ID_HERE",
    "Championship": "YOUR_CHAMPIONSHIP_LEAGUE_ID_HERE", 
    "League I": "YOUR_LEAGUE_I_ID_HERE",
    "League II": "YOUR_LEAGUE_II_ID_HERE",
    "National League": "YOUR_NATIONAL_LEAGUE_ID_HERE"
}
```

Replace each `"YOUR_LEAGUE_ID_HERE"` with your actual league IDs:

```python
LEAGUES = {
    "Premier League": "987654321",
    "Championship": "123456789", 
    "League I": "456789123",
    "League II": "789123456",
    "National League": "321654987"
}
```

## Step 3: Customize League Names (Optional)

You can change the league names to match your setup:

```python
LEAGUES = {
    "316 Premier": "987654321",
    "316 Championship": "123456789", 
    "316 Division One": "456789123",
    "316 Division Two": "789123456",
    "316 National": "321654987"
}
```

## Important Notes:

- **League IDs are numbers only** - don't include quotes around the actual ID
- **Make sure your leagues are public** - private leagues won't work with the API
- **Use current season leagues** - make sure you're using this year's league IDs, not last year's
- **Test one league first** - you can start with just one league ID to test, then add the others

## Example of a Completed Configuration:

```python
LEAGUES = {
    "Premier League": "987654321",
    "Championship": "123456789", 
    "League I": "456789123",
    "League II": "789123456",
    "National League": "321654987"
}
```

After making these changes, save the file and your dashboard will be ready to go!
