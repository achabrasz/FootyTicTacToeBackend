import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# Replace with your actual RapidAPI Key from apidojo
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")

if not RAPIDAPI_KEY:
    raise ValueError("No RAPIDAPI_KEY set in Environment Variables!")
HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "transfermarkt-api.p.rapidapi.com"
}


@app.route('/verify', methods=['GET'])
def verify_player_club():
    player_name = request.args.get('player')
    club_name = request.args.get('club')

    if not player_name or not club_name:
        return jsonify({"error": "Missing player or club parameter"}), 400

    try:
        # Step 1: Search for the Player ID
        search_url = "https://transfermarkt-api.p.rapidapi.com/players/search"
        search_params = {"query": player_name, "domain": "com"}
        search_response = requests.get(search_url, headers=HEADERS, params=search_params).json()

        if not search_response.get('results'):
            return jsonify({"played": False, "reason": "Player not found"}), 404

        player_id = search_response['results'][0]['id']

        # Step 2: Get Player Transfer/Club History
        history_url = f"https://transfermarkt-api.p.rapidapi.com/players/get-transfer-history"
        history_params = {"id": player_id, "domain": "com"}
        history_response = requests.get(history_url, headers=HEADERS, params=history_params).json()

        # Step 3: Check if club name exists in history
        # History usually contains 'oldClubName' and 'newClubName'
        played_there = False
        for transfer in history_response.get('transfers', []):
            if (club_name.lower() in transfer.get('oldClubName', '').lower() or
                    club_name.lower() in transfer.get('newClubName', '').lower()):
                played_there = True
                break

        return jsonify({
            "player": player_name,
            "club": club_name,
            "played": played_there
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)