import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# TheSportsDB public test key is "3"
# For production, replace this with your own key from their Patreon/site
API_KEY = "3"
BASE_URL = f"https://www.thesportsdb.com/api/v1/json/{API_KEY}"

AVAILABLE_CLUBS = [
    # The Top Tier
    "Real Madrid", "Barcelona", "Manchester United", "Manchester City",
    "Liverpool", "Chelsea", "Arsenal", "Bayern Munich", "Juventus",
    "Inter Milan", "AC Milan", "Paris SG", "Atletico Madrid", "Borussia Dortmund",

    # The Talent Factories
    "Ajax", "Benfica", "Porto", "RB Leipzig", "Monaco", "PSV Eindhoven",

    # Historic & Cult Clubs
    "Tottenham Hotspur", "AS Roma", "Napoli", "Lazio", "Sevilla", "Valencia",
    "Bayer Leverkusen", "Marseille", "Lyon", "Aston Villa", "Newcastle",

    # South American Giants
    "Boca Juniors", "River Plate", "Santos", "Flamengo"
]

NATIONAL_TEAMS = [
    "Brazil", "Argentina", "France", "Germany", "England",
    "Spain", "Portugal", "Netherlands", "Italy", "Belgium",
    "Croatia", "Uruguay", "Morocco", "Japan", "USA", "Mexico"
]

TOP_AVAILABLE_CLUBS = [
    # The Top Tier
    "Real Madrid", "Barcelona", "Manchester United", "Manchester City",
    "Liverpool", "Chelsea", "Arsenal", "Bayern Munich", "Juventus",
    "Inter Milan", "AC Milan", "Paris SG", "Atletico Madrid", "Borussia Dortmund",
    "Tottenham Hotspur"
]

TOP_NATIONAL_TEAMS = [
    "Brazil", "Argentina", "France", "Germany", "England",
    "Spain", "Portugal", "Netherlands", "Italy", "Uruguay"
]

@app.route('/start')
def start():
    return "Welcome to the Football Player Club History API! Use the /verify endpoint to check if a player has played for two clubs."


@app.route('/clubs', methods=['GET'])
def get_clubs():
    return jsonify({"available_clubs": AVAILABLE_CLUBS})


@app.route('/nationalTeams', methods=['GET'])
def get_national_teams():
    return jsonify({"available_national_teams": NATIONAL_TEAMS})


@app.route('/topClubs', methods=['GET'])
def get_top_clubs():
    return jsonify({"available_clubs": AVAILABLE_CLUBS})


@app.route('/topNationalTeams', methods=['GET'])
def get_top_national_teams():
    return jsonify({"available_national_teams": TOP_NATIONAL_TEAMS})


@app.route('/club_badge', methods=['GET'])
def get_club_badge():
    club_name = request.args.get('club')
    try:
        search_url = f"{BASE_URL}/searchteams.php?t={club_name.replace(' ', '_')}"
        data = requests.get(search_url).json()
        if data.get('teams'):
            return data['teams'][0].get('strBadge')
    except:
        return None
    return None


@app.route('/verify', methods=['GET'])
def verify_connection():
    print("Request received at /verify endpoint")
    player_name = request.args.get('player')
    club_one = request.args.get('club1')
    club_two = request.args.get('club2')
    print(f"Player: {player_name}, Club1: {club_one}, Club2: {club_two}")

    if not player_name or not club_one or not club_two:
        return jsonify({"error": "Missing player or club1 or club2"}), 400

    try:
        # Step 1: Search for player to get ID
        search_url = f"{BASE_URL}/searchplayers.php?p={player_name.replace(' ', '_')}"
        search_data = requests.get(search_url).json()

        if not search_data.get('player'):
            return jsonify({"played": False, "reason": "Player not found"}), 404

        player = search_data['player'][0]
        player_id = player['idPlayer']
        current_club = player.get('strTeam', '').lower()

        # Step 2: Get Former Teams
        history_url = f"{BASE_URL}/lookupformerteams.php?id={player_id}"
        history_data = requests.get(history_url).json()

        # Collect all clubs (Current + Former)
        all_clubs = [current_club]
        if history_data.get('formerteams'):
            for team in history_data['formerteams']:
                all_clubs.append(team.get('strFormerTeam', '').lower())

        # Step 3: Check for match
        played_there = any(club_one.lower() in club for club in all_clubs) and any(
            club_two.lower() in club for club in all_clubs)

        return jsonify({
            "player": player['strPlayer'],
            "club1": club_one,
            "club2": club_two,
            "played": played_there,
            "clubs_found": all_clubs
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
