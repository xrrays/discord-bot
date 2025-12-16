from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
import os, json, asyncio

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

    team_names = []
    team_scores = []
    
    for matchup_id, matchup_info in matchups.items():
        if matchup_id == "count":
            continue
        matchup = matchup_info["matchup"]
        teams = matchup["0"]["teams"]

        team_1_name = teams["0"]["team"][0][2]["name"]
        team_1_points = float(teams["0"]["team"][1]["team_points"]["total"])
        team_2_name = teams["1"]["team"][0][2]["name"]
        team_2_points = float(teams["1"]["team"][1]["team_points"]["total"])

        team_names.extend([team_1_name, team_2_name])
        team_scores.extend([team_1_points, team_2_points])

    max_team_length = max(len(name) for name in team_names)
    max_score_length = max(len(f"{score:.2f}") for score in team_scores) 

    output = f"**🏆 Week {lg.current_week()} Scoreboard 🏆**\n```\n"
    for matchup_id, matchup_info in matchups.items():
        if matchup_id == "count":
            continue

        matchup = matchup_info["matchup"]
        teams = matchup["0"]["teams"]

        team_1_name = teams["0"]["team"][0][2]["name"]
        team_1_points = float(teams["0"]["team"][1]["team_points"]["total"])
        team_2_name = teams["1"]["team"][0][2]["name"]
        team_2_points = float(teams["1"]["team"][1]["team_points"]["total"])

        output += (
            f"{team_1_name:<{max_team_length}} {team_1_points:>{max_score_length}.2f}  vs  "
            f"{team_2_name:<{max_team_length}} {team_2_points:>{max_score_length}.2f}\n"
        )

    output += "```"
    await ctx.send(output)

# Option 2
async def points_for_leaderboard(ctx):
    standings_data = lg.standings()
    sorted_teams = sorted(standings_data, key=lambda x: float(x['points_for']), reverse=True)

    max_name_length = max(len(team["name"]) for team in sorted_teams)
    spacing = max_name_length + 4  

    output = "**🏆 Points For Leaderboard 🏆**\n```"
    for rank, team in enumerate(sorted_teams, 1):
        name = team["name"]
        points_for = float(team["points_for"])
        
        rank_spacing = " " if rank < 10 else ""

        output += f"{rank_spacing}{rank}. {name:<{spacing}} {points_for:>8.2f} points\n"

    output += "```"
    await ctx.send(output)

# Option 3
async def average_points_for(ctx):
    standings_data = lg.standings()
    points_for_values = [float(team['points_for']) for team in standings_data]
    mean_points = sum(points_for_values) / len(points_for_values)

    sorted_teams = sorted(standings_data, key=lambda x: float(x['points_for']) - mean_points, reverse=True)

    max_name_length = max(len(team["name"]) for team in sorted_teams)
    spacing = max_name_length + 4  

    output = "**🏆 Points For Above/Below Average Leaderboard 🏆**\n```"
    for rank, team in enumerate(sorted_teams, 1):
        deviation = float(team["points_for"]) - mean_points
        sign = "+" if deviation >= 0 else ""
        rank_spacing = " " if rank < 10 else ""  

        output += f"{rank_spacing}{rank}. {team['name']:<{spacing}} {sign}{deviation:.2f}\n"

    output += "```"
    await ctx.send(output)

# Option 4
async def points_against_leaderboard(ctx):
    standings_data = lg.standings()
    sorted_teams = sorted(standings_data, key=lambda x: float(x["points_against"]), reverse=True)

    max_name_length = max(len(team["name"]) for team in sorted_teams)
    spacing = max_name_length + 4  

    output = "**🏆 Points Against Leaderboard 🏆**\n```"
    for rank, team in enumerate(sorted_teams, 1):
        rank_spacing = " " if rank < 10 else ""  
        output += f"{rank_spacing}{rank}. {team['name']:<{spacing}} {float(team['points_against']):.2f} points against\n"

    output += "```"
    await ctx.send(output)

# Option 5
async def average_points_against(ctx):
    standings_data = lg.standings()
    points_against_values = [float(team['points_against']) for team in standings_data]
    mean_points_against = sum(points_against_values) / len(points_against_values)

    sorted_teams = sorted(standings_data, key=lambda x: float(x['points_against']) - mean_points_against, reverse=True)

    max_name_length = max(len(team["name"]) for team in sorted_teams)
    spacing = max_name_length + 4  

    output = "**🏆 Points Against Above/Below Average Leaderboard 🏆**\n```"
    for rank, team in enumerate(sorted_teams, 1):
        deviation = float(team["points_against"]) - mean_points_against
        sign = "+" if deviation >= 0 else ""
        rank_spacing = " " if rank < 10 else ""  

        output += f"{rank_spacing}{rank}. {team['name']:<{spacing}} {sign}{deviation:.2f}\n"

    output += "```"
    await ctx.send(output)

# Option 6
async def average_margin_of_victory_loss(ctx):
    standings_data = lg.standings()
    current_week = int(lg.current_week())

    sorted_teams = sorted(standings_data, key=lambda x: (float(x["points_for"]) - float(x["points_against"])) / current_week, reverse=True)

    max_name_length = max(len(team["name"]) for team in sorted_teams)
    spacing = max_name_length + 4  

    output = "**🏆 Average Margin of Victory/Loss 🏆**\n```"
    for rank, team in enumerate(sorted_teams, 1):
        avg_margin = (float(team["points_for"]) - float(team["points_against"])) / current_week
        sign = "+" if avg_margin >= 0 else ""
        rank_spacing = " " if rank < 10 else ""  

        output += f"{rank_spacing}{rank}. {team['name']:<{spacing}} {sign}{avg_margin:.2f} avg margin per week\n"

    output += "```"
    await ctx.send(output)

# Option 7
async def standings(ctx):
    standings_data = lg.standings()
    sorted_teams = sorted(standings_data, key=lambda x: int(x["rank"]))

    max_name_length = max(len(team["name"]) for team in sorted_teams)
    spacing = max_name_length + 4  

    output = "**🏆 Current Standings 🏆**\n```"
    for team in sorted_teams:
        rank = int(team["rank"])
        name = team["name"]
        points_for = float(team["points_for"])
        points_against = float(team["points_against"])
        rank_spacing = " " if rank < 10 else ""  

        output += f"{rank_spacing}{rank}. {name:<{spacing}} ({points_for:.2f} PF, {points_against:.2f} PA)\n"

    output += "```"
    await ctx.send(output)

# Option 8
async def standings_vs_points_for_difference(ctx):
    standings_data = lg.standings()
    sorted_standings = sorted(standings_data, key=lambda x: int(x["rank"]))
    sorted_by_points_for = sorted(standings_data, key=lambda x: float(x["points_for"]), reverse=True)
    points_for_ranks = {team["team_key"]: rank + 1 for rank, team in enumerate(sorted_by_points_for)}

    max_name_length = max(len(team["name"]) for team in sorted_standings)
    spacing = max_name_length + 4  

    output = "**📊 Standings vs. Points For Difference 📊**\n```"
    for team in sorted_standings:
        team_key = team["team_key"]
        standings_rank = int(team["rank"])
        points_for_rank = points_for_ranks[team_key]
        rank_difference = standings_rank - points_for_rank
        sign = "+" if rank_difference > 0 else ""
        rank_spacing = " " if standings_rank < 10 else ""  

        diff_spacing = " " if rank_difference == 0 else ""

        output += f"{rank_spacing}{standings_rank}. {team['name']:<{spacing}} {sign}{diff_spacing}{rank_difference}  (Rank {standings_rank} in standings, Rank {points_for_rank} in Points For)\n"

    output += "```"
    await ctx.send(output)

# Option 9
async def records_and_history(ctx):
    print("\n🏆 League Records & History 🏆\n")

    # use only completed weeks (exclude the current in-progress week)
    current_week = int(lg.current_week())
    last_completed_week = current_week - 1

    if last_completed_week < 1:
        await ctx.send("not enough completed weeks to generate records yet.\n")
        return

    lowest_weeks = []        # lowest single-week score
    highest_weeks = []       # most points in a single week
    blowout = None           # biggest blowout
    closest = None           # closest non-tie matchup
    bad_beat = None          # highest score in a loss

    for week in range(1, last_completed_week + 1):
        matchups_data = lg.matchups(week)
        try:
            matchups = matchups_data["fantasy_content"]["league"][1]["scoreboard"]["0"]["matchups"]
        except KeyError:
            continue

        for matchup_id, matchup_info in matchups.items():
            if matchup_id == "count":
                continue

            matchup = matchup_info["matchup"]
            teams = matchup["0"]["teams"]

            # grab both teams
            entries = []
            for i in ("0", "1"):
                team = teams[i]["team"]
                name = team[0][2]["name"]
                points = float(team[1]["team_points"]["total"])
                entries.append({"name": name, "points": points})

            team1, team2 = entries[0], entries[1]

            # track all single-week scores
            for t in (team1, team2):
                entry = {
                    "name": t["name"],
                    "points": t["points"],
                    "week": week,
                }
                highest_weeks.append(entry)
                lowest_weeks.append(entry)

            # skip ties for winner/loser-based records
            if team1["points"] == team2["points"]:
                continue

            if team1["points"] > team2["points"]:
                winner, loser = team1, team2
            else:
                winner, loser = team2, team1

            margin = abs(winner["points"] - loser["points"])

            # biggest blowout
            if blowout is None or margin > blowout["margin"]:
                blowout = {
                    "winner": winner["name"],
                    "loser": loser["name"],
                    "winner_points": winner["points"],
                    "loser_points": loser["points"],
                    "margin": margin,
                    "week": week,
                }

            # closest matchup (non-zero margin)
            if closest is None or margin < closest["margin"]:
                closest = {
                    "winner": winner["name"],
                    "loser": loser["name"],
                    "winner_points": winner["points"],
                    "loser_points": loser["points"],
                    "margin": margin,
                    "week": week,
                }

            # highest score in a loss (bad beat)
            if bad_beat is None or loser["points"] > bad_beat["loser_points"]:
                bad_beat = {
                    "loser": loser["name"],
                    "winner": winner["name"],
                    "loser_points": loser["points"],
                    "winner_points": winner["points"],
                    "margin": margin,
                    "week": week,
                }
            
    # sort and keep top/bottom 3
    highest_weeks = sorted(highest_weeks, key=lambda x: x["points"], reverse=True)[:3]
    lowest_weeks = sorted(lowest_weeks, key=lambda x: x["points"])[:3]

    # build discord message instead of printing
    output = "**🏆 League Records & History 🏆**\n```"

    if highest_weeks:
        output += "\n🔥 Top 3 Highest Single-Week Scores\n"
        for i, hw in enumerate(highest_weeks, 1):
            output += f"{i}. {hw['name']} — {hw['points']:.2f} points (Week {hw['week']})\n"
        
    if lowest_weeks:
        output += "\n🗑️ Top 3 Lowest Single-Week Scores\n"
        for i, lw in enumerate(lowest_weeks, 1):
            output += f"{i}. {lw['name']} — {lw['points']:.2f} points (Week {lw['week']})\n"

    if blowout:
        output += (
            f"\n💥 Biggest Blowout\n"
            f"{blowout['winner']} defeated {blowout['loser']} by a margin of "
            f"{blowout['margin']:.2f}: "
            f"{blowout['winner_points']:.2f} - {blowout['loser_points']:.2f} "
            f"(Week {blowout['week']})\n"
        )

    if closest:
        output += (
            f"\n🤏 Closest Matchup\n"
            f"{closest['winner']} defeated {closest['loser']} by a margin of "
            f"{closest['margin']:.2f}: "
            f"{closest['winner_points']:.2f} - {closest['loser_points']:.2f} "
            f"(Week {closest['week']})\n"
        )

    if bad_beat:
        output += (
            f"\n😵 Highest Score in a Loss\n"
            f"{bad_beat['loser']} scores {bad_beat['loser_points']:.2f} in a loss to "
            f"{bad_beat['winner']}: "
            f"{bad_beat['loser_points']:.2f} - {bad_beat['winner_points']:.2f} "
            f"(Week {bad_beat['week']})\n"
        )

    output += "```"
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
        "9️⃣ Records & History\n"
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
            elif choice == '9':
                await records_and_history(ctx)
            elif choice == '0':
                await ctx.send("exiting fantasy tracker. bye!👋")
                break
            else:
                await ctx.send("invalid choice... ❌ ")        
        except asyncio.TimeoutError:
            await ctx.send("timeout reached. exiting menu. ⏳")
            break
    active_users.remove(ctx.author.id)

# main_menu()
# standings_data = lg.standings()
# print("Raw standings data:", standings_data)

