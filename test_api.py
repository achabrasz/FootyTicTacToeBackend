#!/usr/bin/env python3
"""
Test script for Football Tic Tac Toe Backend API
Run this script to test all endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:5005"

# ANSI color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(name):
    print(f"\n{BLUE}{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}{RESET}")

def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")

def print_error(message):
    print(f"{RED}✗ {message}{RESET}")

def print_info(message):
    print(f"{YELLOW}ℹ {message}{RESET}")

def test_get_clubs():
    print_test("GET /clubs")
    response = requests.get(f"{BASE_URL}/clubs")
    if response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved {len(data['available_clubs'])} clubs")
        print(f"Sample clubs: {data['available_clubs'][:3]}")
    else:
        print_error(f"Failed: {response.status_code}")

def test_get_top_clubs():
    print_test("GET /topClubs")
    response = requests.get(f"{BASE_URL}/topClubs")
    if response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved {len(data['available_clubs'])} top clubs")
    else:
        print_error(f"Failed: {response.status_code}")

def test_create_room():
    print_test("POST /rooms - Create Room")
    payload = {"creatorName": "Test Player 1"}
    response = requests.post(f"{BASE_URL}/rooms", json=payload)
    
    if response.status_code == 201:
        data = response.json()
        print_success(f"Room created!")
        print_info(f"Room Code: {data['roomCode']}")
        print_info(f"Player ID: {data['playerId']}")
        print_info(f"Room ID: {data['roomId']}")
        return data
    else:
        print_error(f"Failed: {response.status_code} - {response.text}")
        return None

def test_get_room(room_code):
    print_test(f"GET /rooms/{room_code} - Get Room Details")
    response = requests.get(f"{BASE_URL}/rooms/{room_code}")
    
    if response.status_code == 200:
        data = response.json()
        print_success("Room details retrieved!")
        print_info(f"Creator: {data['creatorName']}")
        print_info(f"Players in room: {len(data['players'])}")
        print_info(f"Game Started: {data['gameStarted']}")
        return data
    else:
        print_error(f"Failed: {response.status_code}")
        return None

def test_join_room(room_code):
    print_test(f"POST /rooms/{room_code}/join - Join Room")
    payload = {"playerName": "Test Player 2"}
    response = requests.post(f"{BASE_URL}/rooms/{room_code}/join", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print_success("Joined room!")
        print_info(f"New Player ID: {data['playerId']}")
        print_info(f"Total players: {len(data['players'])}")
        return data
    else:
        print_error(f"Failed: {response.status_code} - {response.text}")
        return None

def test_select_club(room_code, player_id, club):
    print_test(f"POST /rooms/{room_code}/select-club - Select Club")
    payload = {"playerId": player_id, "club": club}
    response = requests.post(f"{BASE_URL}/rooms/{room_code}/select-club", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Club selected: {club}")
        print_info(f"Players with clubs:")
        for p in data['updatedPlayers']:
            print_info(f"  - {p['name']}: {p['club']}")
        return data
    else:
        print_error(f"Failed: {response.status_code} - {response.text}")
        return None

def test_start_game(room_code, creator_id):
    print_test(f"POST /rooms/{room_code}/start - Start Game")
    payload = {"playerId": creator_id}
    response = requests.post(f"{BASE_URL}/rooms/{room_code}/start", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print_success("Game started!")
        print_info(f"First Player ID: {data['firstPlayerId']}")
        return data
    else:
        print_error(f"Failed: {response.status_code} - {response.text}")
        return None

def test_verify_guess(room_code, player_id, player_name, club):
    print_test(f"POST /rooms/{room_code}/verify-guess - Verify Guess")
    payload = {
        "playerId": player_id,
        "playerName": player_name,
        "clubName": club
    }
    response = requests.post(f"{BASE_URL}/rooms/{room_code}/verify-guess", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        result = "✓ CORRECT" if data['verified'] else "✗ INCORRECT"
        print_success(f"Guess verified! {result}")
        print_info(f"Player found: {data['playerFound']}")
        if data['playerFound']:
            print_info(f"Clubs found: {', '.join(data['clubsFound'])}")
        print_info(f"Points earned: {data['pointsEarned']}")
        print_info(f"Updated score: {data['updatedScore']}")
        return data
    else:
        print_error(f"Failed: {response.status_code} - {response.text}")
        return None

def test_get_leaderboard(room_code):
    print_test(f"GET /rooms/{room_code}/leaderboard - Get Leaderboard")
    response = requests.get(f"{BASE_URL}/rooms/{room_code}/leaderboard")
    
    if response.status_code == 200:
        data = response.json()
        print_success("Leaderboard retrieved!")
        for player in data['players']:
            print_info(f"#{player['rank']} - {player['name']} ({player['club']}): {player['score']} pts")
        return data
    else:
        print_error(f"Failed: {response.status_code}")
        return None

def test_next_turn(room_code, current_player_id):
    print_test(f"POST /rooms/{room_code}/next-turn - Next Turn")
    payload = {"currentPlayerId": current_player_id}
    response = requests.post(f"{BASE_URL}/rooms/{room_code}/next-turn", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print_success("Turn advanced!")
        print_info(f"Next Player ID: {data['nextPlayerId']}")
        return data
    else:
        print_error(f"Failed: {response.status_code} - {response.text}")
        return None

def test_game_history(room_code):
    print_test(f"GET /rooms/{room_code}/game-history - Game History")
    response = requests.get(f"{BASE_URL}/rooms/{room_code}/game-history")
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Game history retrieved! ({len(data['history'])} guesses)")
        for entry in data['history']:
            result = "✓" if entry['verified'] else "✗"
            print_info(f"  {result} {entry['playerName']} guessed {entry['guessedPlayer']} ({entry['club']}) - {entry['pointsEarned']} pts")
        return data
    else:
        print_error(f"Failed: {response.status_code}")
        return None

def test_delete_room(room_code, creator_id):
    print_test(f"DELETE /rooms/{room_code} - Delete Room")
    payload = {"playerId": creator_id}
    response = requests.delete(f"{BASE_URL}/rooms/{room_code}", json=payload)
    
    if response.status_code == 200:
        print_success("Room deleted!")
        return True
    else:
        print_error(f"Failed: {response.status_code} - {response.text}")
        return False

def main():
    print(f"\n{BLUE}{'='*60}")
    print(f"Football Tic Tac Toe - Backend API Test Suite")
    print(f"{'='*60}{RESET}\n")
    
    # Test getting clubs
    test_get_clubs()
    test_get_top_clubs()
    
    # Full game flow
    print(f"\n{YELLOW}{'='*60}")
    print("FULL GAME FLOW TEST")
    print(f"{'='*60}{RESET}")
    
    # Create room
    room_data = test_create_room()
    if not room_data:
        print_error("Cannot continue without room!")
        return
    
    room_code = room_data['roomCode']
    creator_id = room_data['playerId']
    
    time.sleep(1)
    
    # Get room details
    test_get_room(room_code)
    
    time.sleep(1)
    
    # Join room
    join_data = test_join_room(room_code)
    if not join_data:
        print_error("Cannot continue without joining!")
        return
    
    player2_id = join_data['playerId']
    
    time.sleep(1)
    
    # Select clubs
    test_select_club(room_code, creator_id, "Barcelona")
    time.sleep(0.5)
    test_select_club(room_code, player2_id, "Real Madrid")
    
    time.sleep(1)
    
    # Start game
    start_data = test_start_game(room_code, creator_id)
    if not start_data:
        print_error("Cannot continue without starting game!")
        return
    
    time.sleep(1)
    
    # Make some guesses
    print(f"\n{YELLOW}Making test guesses...{RESET}")
    test_verify_guess(room_code, creator_id, "Cristiano Ronaldo", "Real Madrid")
    time.sleep(1)
    
    test_verify_guess(room_code, player2_id, "Lionel Messi", "Barcelona")
    time.sleep(1)
    
    # Check leaderboard
    test_get_leaderboard(room_code)
    
    time.sleep(1)
    
    # Test next turn
    test_next_turn(room_code, creator_id)
    
    time.sleep(1)
    
    # Get game history
    test_game_history(room_code)
    
    time.sleep(1)
    
    # Delete room
    test_delete_room(room_code, creator_id)
    
    print(f"\n{GREEN}{'='*60}")
    print("Test suite completed!")
    print(f"{'='*60}{RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API. Make sure the server is running at http://localhost:5000")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")

