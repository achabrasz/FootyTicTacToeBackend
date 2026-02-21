import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# TheSportsDB public test key is "3"
# For production, replace this with your own key from their Patreon/site
API_KEY = "3"
BASE_URL = f"https://www.thesportsdb.com/api/v1/json/{API_KEY}"


@app.route('/verify', methods=['GET'])
def verify_connection():
    player_name = request.args.get('player')
    target_club = request.args.get('club')

    if not player_name or not target_club:
        return jsonify({"error": "Missing player or club"}), 400

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
        played_there = any(target_club.lower() in club for club in all_clubs)

        return jsonify({
            "player": player['strPlayer'],
            "target_club": target_club,
            "played": played_there,
            "clubs_found": all_clubs
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)