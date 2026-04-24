import os
import requests
import random
import string
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.sqlite import JSON

app = Flask(__name__)

# Enable CORS for all routes - allow all origins for development
CORS(app, 
     origins="*",
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     supports_credentials=False)  # Set to False to avoid credential issues with wildcard origin

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///footytictactoe.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# TheSportsDB public test key is "3"
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
    "Real Madrid", "Barcelona", "Manchester United", "Manchester City",
    "Liverpool", "Chelsea", "Arsenal", "Bayern Munich", "Juventus",
    "Inter Milan", "AC Milan", "Paris SG", "Atletico Madrid", "Borussia Dortmund",
    "Tottenham Hotspur"
]

TOP_NATIONAL_TEAMS = [
    "Brazil", "Argentina", "France", "Germany", "England",
    "Spain", "Portugal", "Netherlands", "Italy", "Uruguay"
]

# ============== DATABASE MODELS ==============

class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    room_code = db.Column(db.String(8), unique=True, nullable=False, index=True)
    creator_id = db.Column(db.String(50), nullable=False)
    creator_name = db.Column(db.String(100), nullable=False)
    game_started = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    current_turn_player_id = db.Column(db.String(50), nullable=True)
    
    players = db.relationship('Player', back_populates='room', cascade='all, delete-orphan')
    game_history = db.relationship('GameHistory', back_populates='room', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'roomCode': self.room_code,
            'creatorId': self.creator_id,
            'creatorName': self.creator_name,
            'gameStarted': self.game_started,
            'createdAt': self.created_at.isoformat(),
            'currentTurnPlayerId': self.current_turn_player_id,
            'players': [p.to_dict() for p in self.players]
        }

class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    club = db.Column(db.String(100), nullable=True)
    score = db.Column(db.Integer, default=0)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    room = db.relationship('Room', back_populates='players')

    def to_dict(self):
        return {
            'playerId': self.player_id,
            'name': self.name,
            'club': self.club,
            'score': self.score,
            'joinedAt': self.joined_at.isoformat()
        }

class GameHistory(db.Model):
    __tablename__ = 'game_history'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    player_id = db.Column(db.String(50), nullable=False)
    player_name = db.Column(db.String(100), nullable=False)
    guessed_player = db.Column(db.String(100), nullable=False)
    club = db.Column(db.String(100), nullable=False)
    verified = db.Column(db.Boolean, nullable=False)
    points_earned = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    room = db.relationship('Room', back_populates='game_history')

    def to_dict(self):
        return {
            'playerId': self.player_id,
            'playerName': self.player_name,
            'guessedPlayer': self.guessed_player,
            'club': self.club,
            'verified': self.verified,
            'pointsEarned': self.points_earned,
            'timestamp': self.timestamp.isoformat()
        }

# ============== UTILITY FUNCTIONS ==============

def generate_room_code():
    """Generate a unique 6-character room code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not Room.query.filter_by(room_code=code).first():
            return code

def generate_player_id():
    """Generate a unique player ID"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def get_room_or_404(room_code):
    """Helper to get room or return 404"""
    room = Room.query.filter_by(room_code=room_code).first()
    if not room:
        return None, jsonify({"error": "Room not found"}), 404
    return room, None, None

# ============== ORIGINAL ENDPOINTS ==============

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
    return jsonify({"available_clubs": TOP_AVAILABLE_CLUBS})

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
        search_url = f"{BASE_URL}/searchplayers.php?p={player_name.replace(' ', '_')}"
        search_data = requests.get(search_url).json()

        if not search_data.get('player'):
            return jsonify({"played": False, "reason": "Player not found"}), 404

        player = search_data['player'][0]
        player_id = player['idPlayer']
        current_club = player.get('strTeam', '').lower()

        history_url = f"{BASE_URL}/lookupformerteams.php?id={player_id}"
        history_data = requests.get(history_url).json()

        all_clubs = [current_club]
        if history_data.get('formerteams'):
            for team in history_data['formerteams']:
                all_clubs.append(team.get('strFormerTeam', '').lower())

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

# ============== ROOM MANAGEMENT ENDPOINTS ==============

@app.route('/rooms', methods=['POST'])
def create_room():
    """Create a new room"""
    data = request.get_json()
    creator_name = data.get('creatorName')
    
    if not creator_name:
        return jsonify({"error": "Missing creatorName"}), 400
    
    try:
        player_id = generate_player_id()
        room_code = generate_room_code()
        
        room = Room(
            room_code=room_code,
            creator_id=player_id,
            creator_name=creator_name
        )
        
        creator = Player(
            player_id=player_id,
            room=room,
            name=creator_name
        )
        
        db.session.add(room)
        db.session.add(creator)
        db.session.commit()
        
        return jsonify({
            "roomId": room.id,
            "roomCode": room.room_code,
            "playerId": player_id,
            "createdAt": room.created_at.isoformat()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/rooms/<room_code>', methods=['GET'])
def get_room(room_code):
    """Get room details"""
    room, error_response, status_code = get_room_or_404(room_code)
    if error_response:
        return error_response, status_code
    
    return jsonify(room.to_dict()), 200

@app.route('/rooms/<room_code>/join', methods=['POST'])
def join_room(room_code):
    """Join an existing room"""
    room, error_response, status_code = get_room_or_404(room_code)
    if error_response:
        return error_response, status_code
    
    data = request.get_json()
    player_name = data.get('playerName')
    
    if not player_name:
        return jsonify({"error": "Missing playerName"}), 400
    
    # Check if game already started
    if room.game_started:
        return jsonify({"error": "Game has already started"}), 400
    
    # Check for duplicate names
    if any(p.name.lower() == player_name.lower() for p in room.players):
        return jsonify({"error": "Player name already exists in room"}), 400
    
    try:
        player_id = generate_player_id()
        player = Player(
            player_id=player_id,
            room_id=room.id,
            name=player_name
        )
        
        db.session.add(player)
        db.session.commit()
        
        return jsonify({
            "playerId": player_id,
            "roomCode": room.room_code,
            "players": [p.to_dict() for p in room.players]
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/rooms/<room_code>/select-club', methods=['POST'])
def select_club(room_code):
    """Update player's selected club"""
    room, error_response, status_code = get_room_or_404(room_code)
    if error_response:
        return error_response, status_code
    
    data = request.get_json()
    player_id = data.get('playerId')
    club = data.get('club')
    
    if not player_id or not club:
        return jsonify({"error": "Missing playerId or club"}), 400
    
    try:
        player = Player.query.filter_by(player_id=player_id, room_id=room.id).first()
        if not player:
            return jsonify({"error": "Player not found in room"}), 404
        
        player.club = club
        db.session.commit()
        
        return jsonify({
            "success": True,
            "updatedPlayers": [p.to_dict() for p in room.players]
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/rooms/<room_code>/start', methods=['POST'])
def start_game(room_code):
    """Start the game"""
    room, error_response, status_code = get_room_or_404(room_code)
    if error_response:
        return error_response, status_code
    
    data = request.get_json()
    player_id = data.get('playerId')
    
    if not player_id:
        return jsonify({"error": "Missing playerId"}), 400
    
    # Verify requester is the creator
    if room.creator_id != player_id:
        return jsonify({"error": "Only the room creator can start the game"}), 403
    
    # Check all players have selected clubs
    for player in room.players:
        if not player.club:
            return jsonify({"error": f"Player {player.name} has not selected a club"}), 400
    
    if len(room.players) < 2:
        return jsonify({"error": "At least 2 players required to start"}), 400
    
    try:
        room.game_started = True
        room.current_turn_player_id = room.players[0].player_id
        db.session.commit()
        
        return jsonify({
            "success": True,
            "firstPlayerId": room.players[0].player_id
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ============== GAME STATE ENDPOINTS ==============

@app.route('/rooms/<room_code>/verify-guess', methods=['POST'])
def verify_guess(room_code):
    """Submit a player guess (improved with points calculation)"""
    room, error_response, status_code = get_room_or_404(room_code)
    if error_response:
        return error_response, status_code
    
    if not room.game_started:
        return jsonify({"error": "Game has not started"}), 400
    
    data = request.get_json()
    player_id = data.get('playerId')
    player_name = data.get('playerName')
    club_name = data.get('clubName')
    
    if not player_id or not player_name or not club_name:
        return jsonify({"error": "Missing playerId, playerName, or clubName"}), 400
    
    player = Player.query.filter_by(player_id=player_id, room_id=room.id).first()
    if not player:
        return jsonify({"error": "Player not found in room"}), 404
    
    try:
        # Call the TheSportsDB API to verify
        search_url = f"{BASE_URL}/searchplayers.php?p={player_name.replace(' ', '_')}"
        search_data = requests.get(search_url).json()
        
        player_found = False
        clubs_found = []
        points_earned = 0
        verified = False
        
        if search_data.get('player'):
            player_found = True
            api_player = search_data['player'][0]
            player_db_id = api_player['idPlayer']
            current_club = api_player.get('strTeam', '').lower()
            
            clubs_found = [current_club]
            
            # Get former teams
            history_url = f"{BASE_URL}/lookupformerteams.php?id={player_db_id}"
            history_data = requests.get(history_url).json()
            
            if history_data.get('formerteams'):
                for team in history_data['formerteams']:
                    clubs_found.append(team.get('strFormerTeam', '').lower())
            
            # Check if guess is correct
            verified = any(club_name.lower() in club for club in clubs_found)
            points_earned = 10 if verified else 0
            
            player.score += points_earned
        
        # Record in game history
        history_entry = GameHistory(
            room_id=room.id,
            player_id=player_id,
            player_name=player.name,
            guessed_player=player_name,
            club=club_name,
            verified=verified,
            points_earned=points_earned
        )
        
        db.session.add(history_entry)
        db.session.commit()
        
        # Build scores dict
        all_players_scores = {p.player_id: p.score for p in room.players}
        
        return jsonify({
            "verified": verified,
            "playerFound": player_found,
            "clubsFound": clubs_found,
            "pointsEarned": points_earned,
            "updatedScore": player.score,
            "allPlayersScores": all_players_scores
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/rooms/<room_code>/next-turn', methods=['POST'])
def next_turn(room_code):
    """Move to next player's turn"""
    room, error_response, status_code = get_room_or_404(room_code)
    if error_response:
        return error_response, status_code
    
    if not room.game_started:
        return jsonify({"error": "Game has not started"}), 400
    
    data = request.get_json()
    current_player_id = data.get('currentPlayerId')
    
    if not current_player_id:
        return jsonify({"error": "Missing currentPlayerId"}), 400
    
    try:
        # Find current player index
        current_idx = None
        for idx, p in enumerate(room.players):
            if p.player_id == current_player_id:
                current_idx = idx
                break
        
        if current_idx is None:
            return jsonify({"error": "Current player not found"}), 404
        
        # Calculate next player
        next_idx = (current_idx + 1) % len(room.players)
        next_player = room.players[next_idx]
        
        room.current_turn_player_id = next_player.player_id
        db.session.commit()
        
        all_scores = {p.player_id: p.score for p in room.players}
        
        return jsonify({
            "nextPlayerId": next_player.player_id,
            "allScores": all_scores
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/rooms/<room_code>/leaderboard', methods=['GET'])
def get_leaderboard(room_code):
    """Get current leaderboard"""
    room, error_response, status_code = get_room_or_404(room_code)
    if error_response:
        return error_response, status_code
    
    try:
        # Sort players by score (descending)
        sorted_players = sorted(room.players, key=lambda p: p.score, reverse=True)
        
        leaderboard = []
        for rank, player in enumerate(sorted_players, 1):
            leaderboard.append({
                "playerId": player.player_id,
                "name": player.name,
                "club": player.club,
                "score": player.score,
                "rank": rank
            })
        
        return jsonify({"players": leaderboard}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/rooms/<room_code>/game-history', methods=['GET'])
def get_game_history(room_code):
    """Get past guesses in the current game"""
    room, error_response, status_code = get_room_or_404(room_code)
    if error_response:
        return error_response, status_code
    
    try:
        history = GameHistory.query.filter_by(room_id=room.id).order_by(
            GameHistory.timestamp.desc()
        ).all()
        
        return jsonify({
            "history": [h.to_dict() for h in history]
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============== DATA MANAGEMENT ENDPOINTS ==============

@app.route('/rooms/<room_code>', methods=['DELETE'])
def delete_room(room_code):
    """Close/delete a room"""
    room, error_response, status_code = get_room_or_404(room_code)
    if error_response:
        return error_response, status_code
    
    data = request.get_json()
    player_id = data.get('playerId')
    
    if not player_id:
        return jsonify({"error": "Missing playerId"}), 400
    
    # Verify requester is the creator
    if room.creator_id != player_id:
        return jsonify({"error": "Only the room creator can close the room"}), 403
    
    try:
        db.session.delete(room)
        db.session.commit()
        
        return jsonify({"success": True}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ============== ERROR HANDLERS & DB INITIALIZATION ==============

@app.before_request
def create_tables():
    """Create database tables if they don't exist"""
    db.create_all()

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5005, debug=True)
