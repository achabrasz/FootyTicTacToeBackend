# Football Tic Tac Toe - Backend

A production-ready Flask backend for a multiplayer football player guessing game. Players create rooms, select clubs, and guess which football players have played for those clubs.

## Features

✅ **Room Management**
- Create private game rooms with unique 6-character codes
- Join existing rooms with player validation
- Support for 2+ players per game
- Creator-only controls for starting and closing games

✅ **Player Management**
- Unique player IDs per game session
- Score tracking and leaderboard
- Club selection per player

✅ **Game State**
- Persistent game state on the server
- Turn-based gameplay with automatic rotation
- Real-time score updates
- Complete game history and statistics

✅ **TheSportsDB Integration**
- Verify player club history automatically
- Support for current and former clubs
- Correct/incorrect guess detection

✅ **Database Support**
- SQLite for development (default)
- PostgreSQL, MySQL, etc. for production
- Persistent room and game data
- Full relational data model

## Quick Start

### Prerequisites
- Python 3.7+
- pip

### Installation

1. Clone/navigate to the backend directory:
```bash
cd Backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Configure environment:
```bash
cp .env.example .env
# Edit .env if needed (defaults work fine for development)
```

### Running the Server

```bash
python app.py
```

The API will be available at: `http://localhost:5000`

### Testing the API

In a separate terminal:
```bash
python test_api.py
```

This will run through a complete game flow and test all endpoints.

## Project Structure

```
Backend/
├── app.py                      # Main Flask application with all endpoints
├── requirements.txt            # Python dependencies
├── API_DOCUMENTATION.md        # Comprehensive API reference
├── test_api.py                # Test suite for all endpoints
├── .env.example               # Environment variables template
├── README.md                  # This file
└── footytictactoe.db          # SQLite database (created on first run)
```

## API Endpoints Overview

### Original Endpoints
- `GET /start` - Welcome message
- `GET /clubs` - Available clubs
- `GET /topClubs` - Top-tier clubs
- `GET /nationalTeams` - National teams
- `GET /topNationalTeams` - Top national teams
- `GET /club_badge` - Club badge image URL
- `GET /verify` - Verify player club history (single guess)

### Room Management
- `POST /rooms` - Create new room
- `GET /rooms/:roomCode` - Get room details
- `POST /rooms/:roomCode/join` - Join existing room
- `POST /rooms/:roomCode/select-club` - Select club for player
- `POST /rooms/:roomCode/start` - Start the game
- `DELETE /rooms/:roomCode` - Close/delete room

### Game State
- `POST /rooms/:roomCode/verify-guess` - Submit player guess
- `POST /rooms/:roomCode/next-turn` - Advance to next player
- `GET /rooms/:roomCode/leaderboard` - Get current scores
- `GET /rooms/:roomCode/game-history` - Get all guesses made

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed endpoint documentation.

## Game Flow Example

```python
# 1. Create room
POST /rooms
{"creatorName": "John Doe"}
→ {"roomCode": "ABC123", "playerId": "...", ...}

# 2. Other players join
POST /rooms/ABC123/join
{"playerName": "Jane Smith"}
→ {"playerId": "...", "players": [...]}

# 3. All players select clubs
POST /rooms/ABC123/select-club
{"playerId": "...", "club": "Real Madrid"}

# 4. Creator starts game
POST /rooms/ABC123/start
{"playerId": "..."}

# 5. Players take turns guessing
POST /rooms/ABC123/verify-guess
{"playerId": "...", "playerName": "Cristiano Ronaldo", "clubName": "Real Madrid"}
→ {"verified": true, "pointsEarned": 10, "updatedScore": 10, ...}

# 6. Get leaderboard
GET /rooms/ABC123/leaderboard
→ {"players": [{"rank": 1, "name": "John Doe", "score": 20, ...}]}

# 7. View game history
GET /rooms/ABC123/game-history
→ {"history": [{"playerName": "John Doe", "guessedPlayer": "...", "verified": true, ...}]}
```

## Database Models

### Room
- Unique room codes for joining
- Creator info and game state
- Current turn tracking
- Relationships to players and game history

### Player
- Unique player IDs per game
- Player names and selected clubs
- Score tracking
- Join timestamps

### GameHistory
- Records all guesses made
- Verification results
- Points earned per guess
- Complete game audit trail

## Configuration

### Environment Variables

Create a `.env` file (or copy from `.env.example`):

```env
# Flask
FLASK_ENV=development
FLASK_DEBUG=True

# Database (default: SQLite)
DATABASE_URL=sqlite:///footytictactoe.db

# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/footytictactoe

# Server
PORT=5000
HOST=0.0.0.0
```

## Development vs Production

### Development
```bash
# Uses SQLite database
# Flask debug mode enabled
python app.py
```

### Production
1. Configure PostgreSQL or MySQL:
```bash
# .env
DATABASE_URL=postgresql://user:password@host/footytictactoe
FLASK_ENV=production
FLASK_DEBUG=False
```

2. Use Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

3. (Optional) Use Procfile for Heroku deployment:
```
web: gunicorn app:app
```

## Scoring System

- **Correct Guess**: 10 points
  - Player name found in TheSportsDB
  - Player has played for the specified club (current or former)
  
- **Incorrect Guess**: 0 points
  - Player not found, OR
  - Player has not played for the specified club

## Features & Capabilities

### Player Verification
- Checks TheSportsDB for player existence
- Retrieves current club
- Retrieves all former clubs
- Case-insensitive matching

### Room Management
- Unique 6-character room codes (alphanumeric)
- Duplicate name prevention
- Automatic club selection validation
- Minimum 2 players required to start

### Game State
- Server-side game state persistence
- Turn-based rotation
- Complete game history audit trail
- Leaderboard with rankings
- Timestamp tracking for all events

## Future Enhancements

### Short Term
- [ ] Rate limiting on `/verify` endpoint
- [ ] Caching player lookups
- [ ] Player statistics API
- [ ] Difficulty levels (more/fewer clubs)

### Medium Term
- [ ] WebSocket support for real-time updates
- [ ] User authentication
- [ ] Lifetime player statistics
- [ ] Favorite clubs management

### Long Term
- [ ] Multi-match tournaments
- [ ] Achievement badges
- [ ] Social features (friends, invites)
- [ ] Mobile app integration
- [ ] Analytics dashboard

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
PORT=5001 python app.py
```

### Database Issues
```bash
# Reset database (WARNING: Deletes all data)
rm footytictactoe.db
python app.py
```

### Room Code Collision
Room codes are automatically regenerated if collision detected. Extremely rare with 36^6 possible combinations.

## API Testing

### Using cURL

```bash
# Create room
curl -X POST http://localhost:5000/rooms \
  -H "Content-Type: application/json" \
  -d '{"creatorName": "John"}'

# Join room
curl -X POST http://localhost:5000/rooms/ABC123/join \
  -H "Content-Type: application/json" \
  -d '{"playerName": "Jane"}'

# Make guess
curl -X POST http://localhost:5000/rooms/ABC123/verify-guess \
  -H "Content-Type: application/json" \
  -d '{
    "playerId": "...",
    "playerName": "Cristiano Ronaldo",
    "clubName": "Real Madrid"
  }'
```

### Using Python Test Suite

```bash
python test_api.py
```

### Using Postman

Import the following collection:
- [Link to Postman collection - to be created]

## Database Schema

### rooms table
```sql
CREATE TABLE rooms (
  id INTEGER PRIMARY KEY,
  room_code VARCHAR(8) UNIQUE NOT NULL,
  creator_id VARCHAR(50) NOT NULL,
  creator_name VARCHAR(100) NOT NULL,
  game_started BOOLEAN DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  current_turn_player_id VARCHAR(50)
);
```

### players table
```sql
CREATE TABLE players (
  id INTEGER PRIMARY KEY,
  player_id VARCHAR(50) UNIQUE NOT NULL,
  room_id INTEGER NOT NULL,
  name VARCHAR(100) NOT NULL,
  club VARCHAR(100),
  score INTEGER DEFAULT 0,
  joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (room_id) REFERENCES rooms(id)
);
```

### game_history table
```sql
CREATE TABLE game_history (
  id INTEGER PRIMARY KEY,
  room_id INTEGER NOT NULL,
  player_id VARCHAR(50) NOT NULL,
  player_name VARCHAR(100) NOT NULL,
  guessed_player VARCHAR(100) NOT NULL,
  club VARCHAR(100) NOT NULL,
  verified BOOLEAN NOT NULL,
  points_earned INTEGER DEFAULT 0,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (room_id) REFERENCES rooms(id)
);
```

## Performance Considerations

- Room codes: O(1) lookup with index
- Player queries: O(1) by player_id or O(n) for room players
- Game history: O(n) retrieval, ordered by timestamp (can add pagination)
- TheSportsDB calls: Rate limited by external API

### Optimization Tips
1. Add database connection pooling for production
2. Implement caching for player lookups
3. Add pagination to game history endpoint
4. Use read replicas for leaderboard queries
5. Monitor TheSportsDB API usage

## License

[Add your license here]

## Support

For issues or questions:
1. Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
2. Review error messages in server logs
3. Test with [test_api.py](test_api.py)
4. [Create an issue/contact support]

## Contributing

[Add contribution guidelines]

---

**Last Updated**: April 2026
**Backend Version**: 2.0 (Production Ready)

