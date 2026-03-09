from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///snake_game.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Data models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    score = db.Column(db.Integer, default=0)
    snake_length = db.Column(db.Integer, default=1)

class GameState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    snake_position = db.Column(db.PickleType, nullable=False)  # List of tuples
    score = db.Column(db.Integer, default=0)

# Schemas
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

class GameStateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = GameState

# Initialize database
@app.before_first_request
def create_tables():
    db.create_all()

# API Endpoints
@app.route('/api/game/start', methods=['POST'])
def start_game():
    username = request.json.get('username')
    if not username:
        return jsonify({"error": "Username is required"}), 400

    new_user = User(username=username)
    db.session.add(new_user)
    db.session.commit()

    new_game_state = GameState(user_id=new_user.id, snake_position=[(5, 5)])  # Sample starting position
    db.session.add(new_game_state)
    db.session.commit()

    return jsonify({"message": "Game started", "user_id": new_user.id}), 201

@app.route('/api/game/move', methods=['PUT'])
def move_snake():
    user_id = request.json.get('user_id')
    direction = request.json.get('direction')

    if not user_id or not direction:
        return jsonify({"error": "User ID and direction are required"}), 400

    game_state = GameState.query.filter_by(user_id=user_id).first()
    user = User.query.get(user_id)

    if not game_state or not user:
        return jsonify({"error": "User or game state not found"}), 404

    # Update snake position logic
    snake_position = game_state.snake_position
    head_x, head_y = snake_position[0]

    if direction == "up":
        new_head = (head_x, head_y - 1)
    elif direction == "down":
        new_head = (head_x, head_y + 1)
    elif direction == "left":
        new_head = (head_x - 1, head_y)
    elif direction == "right":
        new_head = (head_x + 1, head_y)
    else:
        return jsonify({"error": "Invalid direction"}), 400

    # Update game state
    if len(snake_position) >= user.snake_length:  # Snake length
        snake_position.pop()  # Remove tail
    snake_position.insert(0, new_head)  # Add new head

    game_state.snake_position = snake_position
    game_state.score += 1
    db.session.commit()

    return jsonify({"snake_position": game_state.snake_position, "score": game_state.score}), 200

@app.route('/api/game/status', methods=['GET'])
def get_game_status():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    game_state = GameState.query.filter_by(user_id=user_id).first()

    if not game_state:
        return jsonify({"error": "Game state not found"}), 404

    return jsonify({
        "snake_position": game_state.snake_position,
        "score": game_state.score
    }), 200

@app.route('/api/game/end', methods=['POST'])
def end_game():
    user_id = request.json.get('user_id')

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user = User.query.get(user_id)

    if user:
        # Update user's highest score
        game_state = GameState.query.filter_by(user_id=user_id).first()
        if game_state and game_state.score > user.score:
            user.score = game_state.score
            db.session.commit()
            return jsonify({"message": "Game ended and high score updated"}), 200

    return jsonify({"error": "User not found"}), 404

# Run the application
if __name__ == '__main__':
    app.run(debug=True)