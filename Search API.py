#Search API

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///search.db'
db = SQLAlchemy(app)

# Journalist model
class Journalist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    profile = db.Column(db.String(255), nullable=False)

# Post model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    journalist_id = db.Column(db.Integer, db.ForeignKey('journalist.id'), nullable=False)

# Initialize the database
with app.app_context():
    db.create_all()

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])

    journalists = Journalist.query.filter(Journalist.name.like(f'%{query}%') | Journalist.profile.like(f'%{query}%')).all()
    posts = Post.query.filter(Post.title.like(f'%{query}%') | Post.content.like(f'%{query}%')).all()
    
    results = {
        'journalists': [{'id': j.id, 'name': j.name, 'profile': j.profile} for j in journalists],
        'posts': [{'id': p.id, 'title': p.title, 'content': p.content, 'journalist_id': p.journalist_id} for p in posts]
    }
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
