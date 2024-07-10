#Login API

from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
auth = HTTPBasicAuth()

# In-memory user store
users = {
    "admin": generate_password_hash("secret"),
    "user": generate_password_hash("password")
}

# In-memory items for search
items = [
    {"id": 1, "name": "Apple", "description": "A red fruit"},
    {"id": 2, "name": "Banana", "description": "A yellow fruit"},
    {"id": 3, "name": "Cherry", "description": "A small red fruit"}
]

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

@app.route('/search', methods=['GET'])
def search_items():
    query = request.args.get('q', '')
    results = [item for item in items if query.lower() in item['name'].lower() or query.lower() in item['description'].lower()]
    return jsonify(results)

@app.route('/secure-search', methods=['GET'])
@auth.login_required
def secure_search_items():
    query = request.args.get('q', '')
    results = [item for item in items if query.lower() in item['name'].lower() or query.lower() in item['description'].lower()]
    return jsonify(results)

@app.route('/login', methods=['GET'])
@auth.login_required
def login():
    return jsonify({"message": "Logged in as {}".format(auth.current_user())})

if __name__ == '__main__':
    app.run(debug=True)
