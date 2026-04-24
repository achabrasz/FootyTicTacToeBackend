# Football Tic Tac Toe - Backend API Documentation

## Overview
This API provides a complete backend for multiplayer football player guessing games with persistent rooms, player management, scoring, and game history.

## Base URL
```
http://localhost:5000
```

---

## Database Models

### Room
Represents a multiplayer game room.
- `id` - Unique identifier
- `room_code` - 6-character unique code for joining (e.g., "ABC123")
- `creator_id` - Player ID of the room creator
- `creator_name` - Name of the room creator
- `game_started` - Boolean indicating if the game has started
- `created_at` - Timestamp of room creation
- `current_turn_player_id` - Player ID whose turn it currently is

### Player
Represents a player in a room.
- `id` - Unique identifier
- `player_id` - 16-character unique ID for the player (returned on join)
- `room_id` - Foreign key to Room
- `name` - Player's display name
- `club` - Selected club for this game
- `score` - Current points in the game
- `joined_at` - Timestamp when player joined

### GameHistory
Records all guesses made during a game.
- `id` - Unique identifier
- `room_id` - Foreign key to Room
- `player_id` - Player who made the guess
- `player_name` - Player's name at time of guess
- `guessed_player` - Football player name that was guessed
- `club` - Club that was being guessed
- `verified` - Boolean whether the guess was correct
- `points_earned` - Points awarded for this guess (0 or 10)
- `timestamp` - When the guess was made

---

## API Endpoints

### Original Endpoints

#### GET /start
Welcome message and API overview.
```
Response:
"Welcome to the Football Player Club History API! Use the /verify endpoint to check if a player has played for two clubs."
```

#### GET /clubs
Get available clubs for selection.
```
Response:
{
  "available_clubs": [
    "Real Madrid",
    "Barcelona",
    ...
  ]
}
```

#### GET /topClubs
Get top-tier clubs only.
```
Response:
{
  "available_clubs": [
    "Real Madrid",
    "Barcelona",
    ...
  ]
}
```

#### GET /nationalTeams
Get available national teams.
```
Response:
{
  "available_national_teams": [
    "Brazil",
    "Argentina",
    ...
  ]
}
```

#### GET /topNationalTeams
Get top national teams.
```
Response:
{
  "available_national_teams": [
    "Brazil",
    "Argentina",
    ...
  ]
}
```

#### GET /club_badge
Get badge URL for a club.
```
Parameters:
  - club (string): Club name

Response:
URL string to club badge image
```

#### GET /verify
Verify if a player has played for two clubs (original single-guess endpoint).
```
Parameters:
  - player (string): Player name
  - club1 (string): First club name
  - club2 (string): Second club name

Response:
{
  "player": "string",
  "club1": "string",
  "club2": "string",
  "played": boolean,
  "clubs_found": [string]
}
```

---

### Room Management Endpoints

#### POST /rooms
Create a new game room.
```
Request Body:
{
  "creatorName": "John Doe"
}

Response (201 Created):
{
  "roomId": 1,
  "roomCode": "ABC123",
  "playerId": "a1b2c3d4e5f6g7h8",
  "createdAt": "2026-04-24T10:30:00"
}
```

#### GET /rooms/:roomCode
Fetch room details and current player list.
```
Parameters:
  - roomCode (string): The room code (e.g., "ABC123")

Response (200):
{
  "roomCode": "ABC123",
  "creatorId": "a1b2c3d4e5f6g7h8",
  "creatorName": "John Doe",
  "gameStarted": false,
  "createdAt": "2026-04-24T10:30:00",
  "currentTurnPlayerId": null,
  "players": [
    {
      "playerId": "a1b2c3d4e5f6g7h8",
      "name": "John Doe",
      "club": null,
      "score": 0,
      "joinedAt": "2026-04-24T10:30:00"
    }
  ]
}

Error Responses:
404 - Room not found
```

#### POST /rooms/:roomCode/join
Join an existing room.
```
Parameters:
  - roomCode (string): The room code

Request Body:
{
  "playerName": "Jane Smith"
}

Response (200):
{
  "playerId": "x9y8z7w6v5u4t3s2",
  "roomCode": "ABC123",
  "players": [
    {
      "playerId": "a1b2c3d4e5f6g7h8",
      "name": "John Doe",
      "club": null,
      "score": 0,
      "joinedAt": "2026-04-24T10:30:00"
    },
    {
      "playerId": "x9y8z7w6v5u4t3s2",
      "name": "Jane Smith",
      "club": null,
      "score": 0,
      "joinedAt": "2026-04-24T10:35:00"
    }
  ]
}

Error Responses:
404 - Room not found
400 - Missing playerName
400 - Game has already started
400 - Player name already exists in room
```

#### POST /rooms/:roomCode/select-club
Update a player's selected club.
```
Parameters:
  - roomCode (string): The room code

Request Body:
{
  "playerId": "x9y8z7w6v5u4t3s2",
  "club": "Real Madrid"
}

Response (200):
{
  "success": true,
  "updatedPlayers": [
    {
      "playerId": "a1b2c3d4e5f6g7h8",
      "name": "John Doe",
      "club": "Barcelona",
      "score": 0,
      "joinedAt": "2026-04-24T10:30:00"
    },
    {
      "playerId": "x9y8z7w6v5u4t3s2",
      "name": "Jane Smith",
      "club": "Real Madrid",
      "score": 0,
      "joinedAt": "2026-04-24T10:35:00"
    }
  ]
}

Error Responses:
404 - Room not found
404 - Player not found in room
400 - Missing playerId or club
```

#### POST /rooms/:roomCode/start
Start the game (only creator can start).
```
Parameters:
  - roomCode (string): The room code

Request Body:
{
  "playerId": "a1b2c3d4e5f6g7h8"
}

Response (200):
{
  "success": true,
  "firstPlayerId": "a1b2c3d4e5f6g7h8"
}

Error Responses:
404 - Room not found
403 - Only the room creator can start the game
400 - Player [name] has not selected a club
400 - At least 2 players required to start
400 - Missing playerId
```

#### DELETE /rooms/:roomCode
Close/delete a room (only creator can delete).
```
Parameters:
  - roomCode (string): The room code

Request Body:
{
  "playerId": "a1b2c3d4e5f6g7h8"
}

Response (200):
{
  "success": true
}

Error Responses:
404 - Room not found
403 - Only the room creator can close the room
400 - Missing playerId
```

---

### Game State Endpoints

#### POST /rooms/:roomCode/verify-guess
Submit and verify a player guess.
```
Parameters:
  - roomCode (string): The room code

Request Body:
{
  "playerId": "a1b2c3d4e5f6g7h8",
  "playerName": "Cristiano Ronaldo",
  "clubName": "Real Madrid"
}

Response (200):
{
  "verified": true,
  "playerFound": true,
  "clubsFound": ["manchester united", "real madrid", "juventus", "sporting cp"],
  "pointsEarned": 10,
  "updatedScore": 30,
  "allPlayersScores": {
    "a1b2c3d4e5f6g7h8": 30,
    "x9y8z7w6v5u4t3s2": 20
  }
}

If player not found:
{
  "verified": false,
  "playerFound": false,
  "clubsFound": [],
  "pointsEarned": 0,
  "updatedScore": 0,
  "allPlayersScores": { ... }
}

Error Responses:
404 - Room not found
400 - Game has not started
404 - Player not found in room
400 - Missing playerId, playerName, or clubName
```

#### POST /rooms/:roomCode/next-turn
Advance to the next player's turn.
```
Parameters:
  - roomCode (string): The room code

Request Body:
{
  "currentPlayerId": "a1b2c3d4e5f6g7h8"
}

Response (200):
{
  "nextPlayerId": "x9y8z7w6v5u4t3s2",
  "allScores": {
    "a1b2c3d4e5f6g7h8": 30,
    "x9y8z7w6v5u4t3s2": 20
  }
}

Error Responses:
404 - Room not found
400 - Game has not started
404 - Current player not found
400 - Missing currentPlayerId
```

#### GET /rooms/:roomCode/leaderboard
Get the current game leaderboard (sorted by score).
```
Parameters:
  - roomCode (string): The room code

Response (200):
{
  "players": [
    {
      "playerId": "a1b2c3d4e5f6g7h8",
      "name": "John Doe",
      "club": "Barcelona",
      "score": 30,
      "rank": 1
    },
    {
      "playerId": "x9y8z7w6v5u4t3s2",
      "name": "Jane Smith",
      "club": "Real Madrid",
      "score": 20,
      "rank": 2
    }
  ]
}

Error Responses:
404 - Room not found
```

#### GET /rooms/:roomCode/game-history
Get all guesses made in the current game.
```
Parameters:
  - roomCode (string): The room code

Response (200):
{
  "history": [
    {
      "playerId": "a1b2c3d4e5f6g7h8",
      "playerName": "John Doe",
      "guessedPlayer": "Cristiano Ronaldo",
      "club": "Real Madrid",
      "verified": true,
      "pointsEarned": 10,
      "timestamp": "2026-04-24T10:40:00"
    },
    {
      "playerId": "x9y8z7w6v5u4t3s2",
      "playerName": "Jane Smith",
      "guessedPlayer": "Lionel Messi",
      "club": "Barcelona",
      "verified": true,
      "pointsEarned": 10,
      "timestamp": "2026-04-24T10:41:00"
    }
  ]
}

Error Responses:
404 - Room not found
```

---

## Game Flow Example

### 1. Create Room
```bash
curl -X POST http://localhost:5000/rooms \
  -H "Content-Type: application/json" \
  -d '{"creatorName": "John Doe"}'
```
Response: Get `roomCode` and `playerId` (store both on client)

### 2. Join Room
```bash
curl -X POST http://localhost:5000/rooms/ABC123/join \
  -H "Content-Type: application/json" \
  -d '{"playerName": "Jane Smith"}'
```
Response: Get new `playerId` for this player

### 3. Select Clubs
```bash
# Player 1
curl -X POST http://localhost:5000/rooms/ABC123/select-club \
  -H "Content-Type: application/json" \
  -d '{"playerId": "player1_id", "club": "Barcelona"}'

# Player 2
curl -X POST http://localhost:5000/rooms/ABC123/select-club \
  -H "Content-Type: application/json" \
  -d '{"playerId": "player2_id", "club": "Real Madrid"}'
```

### 4. Start Game
```bash
curl -X POST http://localhost:5000/rooms/ABC123/start \
  -H "Content-Type: application/json" \
  -d '{"playerId": "player1_id"}'
```
Response: Get `firstPlayerId` to determine who goes first

### 5. Make Guesses
```bash
curl -X POST http://localhost:5000/rooms/ABC123/verify-guess \
  -H "Content-Type: application/json" \
  -d '{
    "playerId": "player1_id",
    "playerName": "Cristiano Ronaldo",
    "clubName": "Real Madrid"
  }'
```

### 6. Advance Turn
```bash
curl -X POST http://localhost:5000/rooms/ABC123/next-turn \
  -H "Content-Type: application/json" \
  -d '{"currentPlayerId": "player1_id"}'
```

### 7. Check Leaderboard
```bash
curl http://localhost:5000/rooms/ABC123/leaderboard
```

### 8. View Game History
```bash
curl http://localhost:5000/rooms/ABC123/game-history
```

---

## Implementation Notes

### Scoring System
- Correct guess: **10 points**
- Incorrect guess: **0 points**

### Room Code Format
- 6 characters: Mix of uppercase letters and digits
- Example: "ABC123", "XYZ789"

### Player ID Format
- 16 characters: Mix of uppercase/lowercase letters and digits
- Generated randomly on room creation and player join
- Unique globally across all rooms

### Database
- Default: SQLite (`footytictactoe.db`)
- Can be configured via `DATABASE_URL` environment variable
- Supports PostgreSQL, MySQL, etc.

### Error Handling
- All errors return JSON with `"error"` key
- Status codes follow REST conventions
- Game state is always validated server-side

### Performance Considerations
- Consider caching TheSportsDB player lookups
- Implement rate limiting on `/verify` endpoint
- Add pagination if club list grows large
- Consider WebSockets for real-time updates (future enhancement)

---

## Future Enhancements

1. **WebSocket Support**
   - Real-time game updates without polling
   - Events: `room-joined`, `club-selected`, `game-started`, `turn-changed`, `guess-result`, `score-updated`, `room-closed`

2. **Authentication**
   - User accounts for lifetime statistics
   - Favorite clubs management
   - Password-protected rooms

3. **Caching**
   - Cache player lookups from TheSportsDB
   - Reduce API calls and improve response times

4. **Rate Limiting**
   - Prevent API abuse on `/verify` endpoint
   - Per-IP rate limiting

5. **Analytics**
   - Player statistics tracking
   - Historical game data
   - Most guessed players

6. **Multiplayer Synchronization**
   - Live room state updates
   - Prevent simultaneous turn actions
   - Connection status tracking

