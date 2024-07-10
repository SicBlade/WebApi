#API to return USER data / information 

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change this to a random secret key
db = SQLAlchemy(app)
jwt = JWTManager(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    profile = db.Column(db.String(120), nullable=True)

# Subscription model
class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subscribed_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Initialize the database
with app.app_context():
    db.create_all()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400
    
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity={'id': user.id, 'username': username})
        return jsonify(access_token=access_token), 200
    
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    if user:
        return jsonify(username=user.username, profile=user.profile), 200
    return jsonify({"message": "User not found"}), 404

@app.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    if user:
        data = request.get_json()
        user.profile = data.get('profile', user.profile)
        db.session.commit()
        return jsonify({"message": "Profile updated"}), 200
    return jsonify({"message": "User not found"}), 404

@app.route('/subscriptions', methods=['POST'])
@jwt_required()
def subscribe():
    current_user = get_jwt_identity()
    data = request.get_json()
    subscribed_to_id = data.get('subscribed_to_id')
    
    if not User.query.get(subscribed_to_id):
        return jsonify({"message": "User to subscribe to not found"}), 404
    
    subscription = Subscription(user_id=current_user['id'], subscribed_to_id=subscribed_to_id)
    db.session.add(subscription)
    db.session.commit()
    
    return jsonify({"message": "Subscribed successfully"}), 201

@app.route('/subscriptions', methods=['GET'])
@jwt_required()
def get_subscriptions():
    current_user = get_jwt_identity()
    subscriptions = Subscription.query.filter_by(user_id=current_user['id']).all()
    subscribed_to_users = [User.query.get(sub.subscribed_to_id).username for sub in subscriptions]
    return jsonify(subscribed_to=subscribed_to_users), 200

@app.route('/subscribed_data', methods=['GET'])
@jwt_required()
def get_subscribed_data():
    current_user = get_jwt_identity()
    subscriptions = Subscription.query.filter_by(user_id=current_user['id']).all()
    subscribed_to_ids = [sub.subscribed_to_id for sub in subscriptions]
    subscribed_users = User.query.filter(User.id.in_(subscribed_to_ids)).all()
    data = [{'username': user.username, 'profile': user.profile} for user in subscribed_users]
    return jsonify(subscribed_data=data), 200

if __name__ == '__main__':
    app.run(debug=True)
