from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from marshmallow import Schema, fields, ValidationError
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///snake_game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Swagger Configuration
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Database Models
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GameSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    difficulty = db.Column(db.String(20), nullable=False)
    level = db.Column(db.Integer, nullable=False)

# Schemas for Validation
class ScoreSchema(Schema):
    username = fields.Str(required=True)
    score = fields.Int(required=True)

class GameSettingsSchema(Schema):
    difficulty = fields.Str(required=True)
    level = fields.Int(required=True)

score_schema = ScoreSchema()
scores_schema = ScoreSchema(many=True)
settings_schema = GameSettingsSchema()

# API Endpoints
@app.route('/api/scores', methods=['POST'])
def add_score():
    json_data = request.get_json()
    try:
        data = score_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_score = Score(username=data['username'], score=data['score'])
    db.session.add(new_score)
    db.session.commit()
    return score_schema.jsonify(new_score), 201

@app.route('/api/scores', methods=['GET'])
def get_scores():
    scores = Score.query.all()
    return scores_schema.jsonify(scores)

@app.route('/api/scores/<int:id>', methods=['GET'])
def get_score(id):
    score = Score.query.get_or_404(id)
    return score_schema.jsonify(score)

@app.route('/api/scores/<int:id>', methods=['DELETE'])
def delete_score(id):
    score = Score.query.get_or_404(id)
    db.session.delete(score)
    db.session.commit()
    return jsonify(message="Score deleted"), 204

@app.route('/api/settings', methods=['GET'])
def get_settings():
    settings = GameSettings.query.first()
    if settings:
        return settings_schema.jsonify(settings)
    return jsonify(message="Settings not found"), 404

@app.route('/api/settings', methods=['PUT'])
def update_settings():
    json_data = request.get_json()
    try:
        data = settings_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    settings = GameSettings.query.first()
    if settings:
        settings.difficulty = data['difficulty']
        settings.level = data['level']
        db.session.commit()
        return settings_schema.jsonify(settings)
    else:
        new_settings = GameSettings(**data)
        db.session.add(new_settings)
        db.session.commit()
        return settings_schema.jsonify(new_settings), 201

@app.route('/api/game/start', methods=['POST'])
def start_game():
    return jsonify(message="Game Started"), 200

@app.route('/api/game/stop', methods=['POST'])
def stop_game():
    json_data = request.get_json()
    username = json_data.get("username")
    score = json_data.get("score")
    if not username or score is None:
        return jsonify(message="Invalid data"), 400

    new_score = Score(username=username, score=score)
    db.session.add(new_score)
    db.session.commit()
    return jsonify(message="Game Stopped and Score Saved"), 200

# Initialize Database
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)