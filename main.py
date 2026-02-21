import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# Use the API-Football Host and your Key
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}


@app.route('/verify', methods=['GET'])
def verify():
    player_name = request.args.get('player')
    club_target = request.args.get('club')

    if not player_name or not club_target:
        return jsonify({"error": "Missing params"}), 400

    try:
        # 1. Search for the player to get their ID
        search_url = "https://api-football-v1.p.rapidapi.com/v3/players"
        # We search by name. Note: API-Football often requires a 'search' param of at least 3 chars
        search_params = {"search": player_name}
        search_res = requests.get(search_url, headers=HEADERS, params=search_params).json()

        if not search_res.get('response'):
            return jsonify({"played": False, "reason": "Player not found"}), 404

        # Get the first matching player ID
        player_id = search_res['response'][0]['player']['id']

        # 2. Get all seasons/teams for this player
        # We query the player's info which includes their statistics (and thus their teams)
        # To be safe, we can check the 'transfers' endpoint or just 'players' with seasons
        history_url = "https://api-football-v1.p.rapidapi.com/v3/players"
        # We'll fetch the most recent data; for Tic Tac Toe, you might need to loop seasons
        # but a better endpoint for "all clubs ever" is the 'transfers' endpoint:

        transfer_url = "https://api-football-v1.p.rapidapi.com/v3/transfers"
        transfer_params = {"player": player_id}
        transfer_res = requests.get(transfer_url, headers=HEADERS, params=transfer_params).json()

        played_there = False
        clubs_found = []

        # Check transfer history
        for t in transfer_res.get('response', []):
            in_team = t['teams']['in']['name'].lower()
            out_team = t['teams']['out']['name'].lower()
            clubs_found.extend([in_team, out_team])

            if club_target.lower() in in_team or club_target.lower() in out_team:
                played_there = True
                break

        return jsonify({
            "player": player_name,
            "target_club": club_target,
            "played": played_there,
            "history_snippet": list(set(clubs_found))[:5]  # Show a few for debugging
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)