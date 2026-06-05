import statsapi
import pandas as pd

#MIL Team ID
MIL_TEAM_ID = 158

#ask which season you want
season = input("What season do you want to compare?: ")

#get MIL roster
roster = statsapi.get(
    "team_roster",
    {
        "teamId": MIL_TEAM_ID,
        "rosterType": "active",
        "season": season
    }
)

rows = []

for player in roster["roster"]:
    person = player["person"]
    position = player["position"]

    player_name = person["fullName"]
    player_id = person["id"]
    position_type = position["type"]

    #Only include pitchers
    if position_type != "Pitcher":
        continue

    data = statsapi.player_stat_data(
        player_id,
        group="pitching",
        type="season",
        season=season
    )

    #Some players may not have pitching stats
    if len(data["stats"]) ==0:
        continue

    pitching_stats = data["stats"][0]["stats"]

    era = pitching_stats.get("era")
    baa = pitching_stats.get("avg") or pitching_stats.get("opponentAvg")
    whip = pitching_stats.get("whip")
    innings = pitching_stats.get("inningsPitched")
    games = pitching_stats.get("gamesPlayed")
    strikeouts = pitching_stats.get("strikeOuts")
    walks = pitching_stats.get("baseOnBalls")

    rows.append({
        "Name": player_name,
        "ERA": era,
        "BAA": baa,
        "WHIP": whip,
        "IP": innings,
        "G": games,
        "SO": strikeouts,
        "BB": walks
    })

df = pd.DataFrame(rows)

#Convert number columns from text to actual numbers
df["ERA"] = pd.to_numeric(df["ERA"], errors="coerce")
df["BAA"] = pd.to_numeric(df["BAA"], errors="coerce")
df["WHIP"] = pd.to_numeric(df["WHIP"], errors="coerce")

#Rank Pitchers
#Lower ERA is Better
#Lower BAA is Better
#Lower WHIP is Better
df["ERA Rank"] = df["ERA"].rank(ascending=True)
df["BAA Rank"] = df["BAA"].rank(ascending=True)
df["WHIP Rank"] = df["WHIP"].rank(ascending=True)

#Create a simple overall score
df["Overall Score"] = (df["ERA Rank"] + df["BAA Rank"] + df["WHIP Rank"]) / 3

#Sort best to Worst
df = df.sort_values("Overall Score")

print()
print("Milwaukee Brewers Pitcher Comparison for", season)
print("---------------------------------------------")
print(df)

#save to CSV so you can open in Excel
from datetime import date

file_name = "brewers_pitcher_comparison" + str(date.today()) + ".csv"

df.to_csv(file_name, index=False)

print()
print("Saved as ", file_name)
