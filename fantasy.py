from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
from tabulate import tabulate
import os
import json
import asyncio

oauth_data = {
    "access_token": os.getenv("ACCESS_TOKEN"),
    "consumer_key": os.getenv("CONSUMER_KEY"),
    "consumer_secret": os.getenv("CONSUMER_SECRET"),
    "guid": None,
    "refresh_token": os.getenv("REFRESH_TOKEN"),
    "token_time": float(os.getenv("TOKEN_TIME", "0")),
    "token_type": os.getenv("TOKEN_TYPE")
}
with open("oauth2_env.json", "w") as f:
    json.dump(oauth_data, f)
sc = OAuth2(None, None, from_file="oauth2_env.json")
gm = yfa.Game(sc, 'nhl')
lg = gm.to_league((os.getenv('LEAGUE_ID')))

num_weeks = lg.current_week()
active_users = set()

# Option 1
async def current_week_scoreboard(ctx):
    matchups_data = lg.matchups()
    matchups = matchups_data["fantasy_content"]["league"][1]["scoreboard"]["0"]["matchups"]
    
    output = f"**🏆 Week {num_weeks} Scoreboard 🏆**\n"
    for matchup_id, matchup_info in matchups.items():
        if matchup_id == "count":
            continue
        
        matchup = matchup_info["matchup"]
        teams = matchup["0"]["teams"]
        
        team_1_name = teams["0"]["team"][0][2]["name"]
        team_1_points = teams["0"]["team"][1]["team_points"]["total"]
        team_2_name = teams["1"]["team"][0][2]["name"]
        team_2_points = teams["1"]["team"][1]["team_points"]["total"]

        output += f"{team_1_name:<25} {team_1_points}  vs  {team_2_name:<25} {team_2_points}\n"

    await ctx.send(output)

# Option 2
async def points_for_leaderboard(ctx):
    standings_data = lg.standings()
    sorted_teams = sorted(standings_data, key=lambda x: float(x['points_for']), reverse=True)

    max_name_length = max(len(team["name"]) for team in sorted_teams)
    spacing = max_name_length + 4  

    output = "**🏆 Points For Leaderboard 🏆**\n"
    for rank, team in enumerate(sorted_teams, 1):
        name = team["name"]
        points_for = float(team["points_for"])
        
        output += f"{rank}. {name:<{spacing}} {points_for:>8.2f} points\n"

    await ctx.send(f"```{output}```")  


# Option 3
async def average_points_for(ctx):
    standings_data = lg.standings()
    points_for_values = [float(team['points_for']) for team in standings_data]
    mean_points = sum(points_for_values) / len(points_for_values)

    sorted_teams = sorted(standings_data, key=lambda x: float(x['points_for']) - mean_points, reverse=True)

    max_name_length = max(len(team["name"]) for team in sorted_teams)
    spacing = max_name_length + 4  

    output = "**🏆 Points For Above/Below Average Leaderboard 🏆**\n"
    for rank, team in enumerate(sorted_teams, 1):
        deviation = float(team["points_for"]) - mean_points
        sign = "+" if deviation >= 0 else ""
        output += f"{rank}. {team['name']:<{spacing}} {sign}{deviation:.2f}\n"

    await ctx.send(output)

# Option 4
async def points_against_leaderboard(ctx):
    standings_data = lg.standings()
    sorted_teams = sorted(standings_data, key=lambda x: float(x["points_against"]), reverse=True)

    max_name_length = max(len(team["name"]) for team in sorted_teams)
    spacing = max_name_length + 4  

    output = "**🏆 Points Against Leaderboard 🏆**\n"
    for rank, team in enumerate(sorted_teams, 1):
        output += f"{rank}. {team['name']:<{spacing}} {float(team['points_against']):.2f} points against\n"

    await ctx.send(output)

# Option 5
async def average_points_against(ctx):
    standings_data = lg.standings()
    points_against_values = [float(team['points_against']) for team in standings_data]
    mean_points_against = sum(points_against_values) / len(points_against_values)

    sorted_teams = sorted(standings_data, key=lambda x: float(x['points_against']) - mean_points_against, reverse=True)

    max_name_length = max(len(team["name"]) for team in sorted_teams)
    spacing = max_name_length + 4  

    output = "**🏆 Points Against Above/Below Average Leaderboard 🏆**\n"
    for rank, team in enumerate(sorted_teams, 1):
        deviation = float(team["points_against"]) - mean_points_against
        sign = "+" if deviation >= 0 else ""
        output += f"{rank}. {team['name']:<{spacing}} {sign}{deviation:.2f}\n"

    await ctx.send(output)

# Option 6
async def average_margin_of_victory_loss(ctx):
    standings_data = lg.standings()
    current_week = int(lg.current_week())

    sorted_teams = sorted(standings_data, key=lambda x: (float(x["points_for"]) - float(x["points_against"])) / current_week, reverse=True)

    max_name_length = max(len(team["name"]) for team in sorted_teams)
    spacing = max_name_length + 4  

    output = "**🏆 Average Margin of Victory/Loss 🏆**\n"
    for rank, team in enumerate(sorted_teams, 1):
        avg_margin = (float(team["points_for"]) - float(team["points_against"])) / current_week
        sign = "+" if avg_margin >= 0 else ""
        output += f"{rank}. {team['name']:<{spacing}} {sign}{avg_margin:.2f} avg margin per week\n"

    await ctx.send(output)

# Option 7
async def standings(ctx):
    standings_data = lg.standings()
    sorted_teams = sorted(standings_data, key=lambda x: int(x["rank"]))

    # Calculate proper spacing
    max_name_length = max(len(team["name"]) for team in sorted_teams)
    spacing = max_name_length + 4  # Add padding for even alignment

    output = "**🏆 Current Standings 🏆**\n"
    for team in sorted_teams:
        rank = int(team["rank"])
        name = team["name"]
        points_for = float(team["points_for"])
        points_against = float(team["points_against"])
        
        # Format the output with spacing
        output += f"{rank}. {name:<{spacing}} ({points_for:.2f} PF, {points_against:.2f} PA)\n"

    await ctx.send(output)


# Option 8
async def standings_vs_points_for_difference(ctx):
    standings_data = lg.standings()
    sorted_standings = sorted(standings_data, key=lambda x: int(x["rank"]))
    sorted_by_points_for = sorted(standings_data, key=lambda x: float(x["points_for"]), reverse=True)
    points_for_ranks = {team["team_key"]: rank + 1 for rank, team in enumerate(sorted_by_points_for)}

    max_name_length = max(len(team["name"]) for team in sorted_standings)
    spacing = max_name_length + 4  

    output = "**📊 Standings vs. Points For Difference 📊**\n"
    for team in sorted_standings:
        team_key = team["team_key"]
        standings_rank = int(team["rank"])
        points_for_rank = points_for_ranks[team_key]
        rank_difference = standings_rank - points_for_rank
        sign = "+" if rank_difference > 0 else ""
        output += f"{team['name']:<{spacing}} {sign}{rank_difference}  (Rank {standings_rank} in standings, Rank {points_for_rank} in Points For)\n"

    await ctx.send(output)

async def display_menu(ctx):
    menu = (
        "**🏒 Fantasy Tracker Menu 🏒**\n"
        "1️⃣ Current Week Scoreboard\n"
        "2️⃣ Points For Leaderboard\n"
        "3️⃣ Points For Above/Below Average Leaderboard\n"
        "4️⃣ Points Against Leaderboard\n"
        "5️⃣ Points Against Above/Below Average Leaderboard\n"
        "6️⃣ Average Margin of Victory/Loss\n"
        "7️⃣ Standings\n"
        "8️⃣ Standings vs Points For Difference\n"
        "0️⃣ Exit"
    )
    await ctx.send(menu)

async def main_menu(ctx):
    if ctx.author.id in active_users:
        await ctx.send("you already have an active fantasy session... ⚠️ ")
        return
    active_users.add(ctx.author.id)

    await display_menu(ctx) 

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    while True:
        try:
            msg = await ctx.bot.wait_for("message", check=check, timeout=60.0)
            
            choice = msg.content.strip()
            if choice == '1':
                await current_week_scoreboard(ctx)
            elif choice == '2':
                await points_for_leaderboard(ctx)
            elif choice == '3':
                await average_points_for(ctx)
            elif choice == '4':
                await points_against_leaderboard(ctx)
            elif choice == '5':
                await average_points_against(ctx)
            elif choice == '6':
                await average_margin_of_victory_loss(ctx)
            elif choice == '7':
                await standings(ctx)
            elif choice == '8':
                await standings_vs_points_for_difference(ctx)
            elif choice == '0':
                await ctx.send("exiting fantasy tracker. bye! 👋")
                break
            else:
                await ctx.send("invalid choice... ❌ ")
        
        except asyncio.TimeoutError:
            await ctx.send("timeout reached. exiting menu. ⏳")
            break

    active_users.remove(ctx.author.id)

#main_menu()
#standings_data = lg.standings()
#print("Raw standings data:", standings_data)

