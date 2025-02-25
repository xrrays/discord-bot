from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
from tabulate import tabulate
import os


sc = OAuth2(None, None,
    os.getenv("CONSUMER_KEY"),
    os.getenv("CONSUMER_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    refresh_token=os.getenv("REFRESH_TOKEN"),
    token_time=float(os.getenv("TOKEN_TIME")),
    token_type=os.getenv("TOKEN_TYPE")
)

gm = yfa.Game(sc, 'nhl')
lg = gm.to_league((int(os.getenv('LEAGUE_ID'))))

num_weeks = lg.current_week()  # number of weeks

# Option 1
def current_week_scoreboard():
    print("\n🏆 Current Scoreboard 🏆")
    # fetch matchups
    matchups_data = lg.matchups()
    matchups = matchups_data["fantasy_content"]["league"][1]["scoreboard"]["0"]["matchups"]

    # iterate through each matchup
    for matchup_id, matchup_info in matchups.items():
        if matchup_id == "count":  # ignore 'count' field?
            continue

        matchup = matchup_info["matchup"]
        teams = matchup["0"]["teams"]

        # extract team names and points
        team_1_name = teams["0"]["team"][0][2]["name"]
        team_1_points = teams["0"]["team"][1]["team_points"]["total"]
        team_2_name = teams["1"]["team"][0][2]["name"]
        team_2_points = teams["1"]["team"][1]["team_points"]["total"]

        # print the formatted matchup
        print(f"{team_1_name} ({team_1_points}) vs {team_2_name} ({team_2_points})")

    print("\nEnd of Scoreboard\n")

# Option 2
def points_for_leaderboard():
    print("\n🏆 Points For Leaderboard 🏆")
    
    # fetch standings data
    standings_data = lg.standings()

    # sort teams by points_for in descending order (convert to float for sorting)
    sorted_teams = sorted(
        standings_data, 
        key=lambda x: float(x['points_for']), 
        reverse=True
    )

    for rank, team in enumerate(sorted_teams, 1):
        print(f"{rank}. {team['name']}: {float(team['points_for']):.2f} points")
    
    print("\nEnd of Leaderboard\n")

# Option 3
def average_points_for():
    print("\n🏆 Points For Above/Below Average Leaderboard 🏆")

    standings_data = lg.standings()

    points_for_values = [float(team['points_for']) for team in standings_data]
    mean_points = sum(points_for_values) / len(points_for_values)

    teams_with_deviation = [
        {"name": team["name"], "deviation": float(team["points_for"]) - mean_points}
        for team in standings_data
    ]

    sorted_teams = sorted(teams_with_deviation, key=lambda x: x["deviation"], reverse=True)
    for rank, team in enumerate(sorted_teams, 1):
        sign = "+" if team["deviation"] >= 0 else ""  
        print(f"{rank}. {team['name']}: {sign}{team['deviation']:.2f}")
    
    print("\nEnd of Leaderboard\n")

# Option 4
def points_against_leaderboard():
    print("\n🏆 Points Against Leaderboard 🏆")
    
    standings_data = lg.standings()
    sorted_teams = sorted(standings_data, key=lambda x: float(x["points_against"]), reverse=True)
    for rank, team in enumerate(sorted_teams, 1):
        print(f"{rank}. {team['name']}: {float(team['points_against']):.2f} points against")
    
    print("\nEnd of Leaderboard\n")

# Option 5
def average_points_against():
    print("\n🏆 Points Against Above/Below Average Leaderboard 🏆")

    standings_data = lg.standings()
    points_against_values = [float(team['points_against']) for team in standings_data]
    mean_points_against = sum(points_against_values) / len(points_against_values)

    teams_with_deviation = [
        {"name": team["name"], "deviation": float(team["points_against"]) - mean_points_against}
        for team in standings_data
    ]

    sorted_teams = sorted(teams_with_deviation, key=lambda x: x["deviation"], reverse=True)

    for rank, team in enumerate(sorted_teams, 1):
        sign = "+" if team["deviation"] >= 0 else "" 
        print(f"{rank}. {team['name']}: {sign}{team['deviation']:.2f}")
    
    print("\nEnd of Leaderboard\n")

# Option 6
def average_margin_of_victory_loss():
    print("\n🏆 Average Margin of Victory/Loss Leaderboard 🏆")

    standings_data = lg.standings()
    current_week = int(lg.current_week()) 

    teams_with_margin = [
        {
            "name": team["name"],
            "avg_margin": (float(team["points_for"]) - float(team["points_against"])) / current_week
        }
        for team in standings_data
    ]

    sorted_teams = sorted(teams_with_margin, key=lambda x: x["avg_margin"], reverse=True)
    max_name_length = max(len(team["name"]) for team in sorted_teams)
    spacing = max_name_length + 4 

    for rank, team in enumerate(sorted_teams, 1):
        sign = "+" if team["avg_margin"] >= 0 else "" 
        formatted_team = f"{rank}. {team['name']:<{spacing}}"
        print(f"{formatted_team} {sign}{team['avg_margin']:.2f} avg margin per week")
    
    print("\nEnd of Leaderboard\n")

# Option 7
def standings():
    print("\n🏆 Current Standings 🏆")

    standings_data = lg.standings()

    sorted_teams = sorted(standings_data, key=lambda x: int(x["rank"]))

    table_data = [
        [team["rank"], team["name"], f"{float(team['points_for']):.2f}", f"{float(team['points_against']):.2f}"]
        for team in sorted_teams
    ]

    print(tabulate(table_data, headers=["Rank", "Team Name", "Points For", "Points Against"], tablefmt="grid", numalign="left", stralign="left"))

    print("\nEnd of Standings\n")

# Option 8
def standings_vs_points_for_difference():
    print("\n📊 Standings vs. Points For Difference...")

    standings_data = lg.standings()
    sorted_standings = sorted(standings_data, key=lambda x: int(x["rank"]))
    sorted_by_points_for = sorted(standings_data, key=lambda x: float(x["points_for"]), reverse=True)
    points_for_ranks = {team["team_key"]: rank + 1 for rank, team in enumerate(sorted_by_points_for)}

    results = []
    for team in sorted_standings:
        team_key = team["team_key"]
        standings_rank = int(team["rank"])
        points_for_rank = points_for_ranks[team_key]
        rank_difference = standings_rank - points_for_rank  
        formatted_diff = f" {rank_difference}" if rank_difference == 0 else f"{rank_difference}"  
        results.append((team["name"], formatted_diff, standings_rank, points_for_rank))

    results.sort(key=lambda x: x[2])
    max_team_name_length = max(len(team[0]) for team in results)
    spacing = max_team_name_length + 4  

    print("\n📌 Standings vs. Points For Difference 📌\n")
    for team_name, rank_diff, standings_rank, points_for_rank in results:
        sign = "+" if int(rank_diff) > 0 else ""  
        formatted_team = f"{team_name:<{spacing}}"
        print(f"{formatted_team} {sign}{rank_diff}  (Rank {standings_rank:<2} in standings, Rank {points_for_rank:<2} in Points For)")
    
    print("\nEnd of Leaderboard\n")

def display_menu():
    print("Welcome to the fantasy tracker application for Peeny for Celebrini!")
    print("Choose an option:")
    print("1. Current Week Scoreboard")
    print("2. Points For Leaderboard")
    print("3. Points For Above/Below Average Leaderboard")
    print("4. Points Against Leaderboard")
    print("5. Points For Above/Below Average Leaderboard")
    print("6. Average Margin of Victory/Loss")
    print("7. Standings")
    print("8. Standings vs Points For Difference")
    print("0. Exit")

def main_menu():
    while True:
        display_menu()
        choice = input("Enter your choice: ")
        if choice == '1':
            current_week_scoreboard()
        elif choice == '2':
            points_for_leaderboard()
        elif choice == '3':
            average_points_for()
        elif choice == '4':
            points_against_leaderboard()
        elif choice == '5':
            average_points_against()
        elif choice == '6':
            average_margin_of_victory_loss()
        elif choice == '7':
            standings()
        elif choice == '8':
            standings_vs_points_for_difference()
        elif choice == '0':
            print("Exiting Fantasy Tracker App. Goodbye!")
            break
        else:
            print("Invalid choice, please select a valid option.")

#main_menu()
#standings_data = lg.standings()
#print("Raw standings data:", standings_data)

