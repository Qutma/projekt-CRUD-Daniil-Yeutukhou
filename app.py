from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
db_path = os.path.join(os.path.dirname(__file__), 'movies.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # "Film" или "Serial"
    year = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    watched_date = db.Column(db.String(20), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    movies = Movie.query.all()
    # Автоматический подсчет среднего рейтинга
    average_rating = round(sum(m.rating for m in movies)/len(movies), 2) if movies else 0
    return render_template('index.html', movies=movies, average_rating=average_rating)

@app.route('/add_edit', methods=['GET', 'POST'])
@app.route('/add_edit/<int:id>', methods=['GET', 'POST'])
def add_edit_movie(id=None):
    movie = Movie.query.get(id) if id else None
    if request.method == 'POST':
        if movie:
            movie.title = request.form['title']
            movie.genre = request.form['genre']
            movie.type = request.form['type']
            movie.year = request.form['year']
            movie.rating = request.form['rating']
            movie.comment = request.form['comment']
            movie.watched_date = request.form['watched_date']
        else:
            movie = Movie(
                title=request.form['title'],
                genre=request.form['genre'],
                type=request.form['type'],
                year=request.form['year'],
                rating=request.form['rating'],
                comment=request.form['comment'],
                watched_date=request.form['watched_date']
            )
            db.session.add(movie)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add_edit.html', movie=movie)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_movie(id):
    movie = Movie.query.get_or_404(id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))

# --- API routes ---
@app.route('/movies', methods=['GET'])
def get_movies_api():
    movies = Movie.query.all()
    return jsonify([
        {
            'id': m.id,
            'title': m.title,
            'genre': m.genre,
            'type': m.type,
            'year': m.year,
            'rating': m.rating,
            'comment': m.comment,
            'watched_date': m.watched_date
        } for m in movies
    ])

@app.route('/movies/<int:id>', methods=['GET'])
def get_movie_api(id):
    movie = Movie.query.get(id)
    if not movie:
        return jsonify({'error': 'Movie not found'}), 404
    return jsonify({
        'id': movie.id,
        'title': movie.title,
        'genre': movie.genre,
        'type': movie.type,
        'year': movie.year,
        'rating': movie.rating,
        'comment': movie.comment,
        'watched_date': movie.watched_date
    })

@app.route('/movies', methods=['POST'])
def add_movie_api():
    data = request.get_json()
    required_fields = ['title', 'genre', 'type', 'year', 'rating', 'watched_date']
    if not data or not all(k in data for k in required_fields):
        return jsonify({'error': 'Missing data'}), 400
    new_movie = Movie(
        title=data['title'],
        genre=data['genre'],
        type=data['type'],
        year=data['year'],
        rating=data['rating'],
        comment=data.get('comment'),
        watched_date=data['watched_date']
    )
    db.session.add(new_movie)
    db.session.commit()
    return jsonify({'message': 'Movie added', 'id': new_movie.id}), 201

@app.route('/movies/<int:id>', methods=['PUT'])
def update_movie_api(id):
    movie = Movie.query.get(id)
    if not movie:
        return jsonify({'error': 'Movie not found'}), 404
    data = request.get_json()
    for field in ['title', 'genre', 'type', 'year', 'rating', 'comment', 'watched_date']:
        if field in data:
            setattr(movie, field, data[field])
    db.session.commit()
    return jsonify({'message': 'Movie updated'})

@app.route('/movies/<int:id>', methods=['DELETE'])
def delete_movie_api(id):
    movie = Movie.query.get(id)
    if not movie:
        return jsonify({'error': 'Movie not found'}), 404
    db.session.delete(movie)
    db.session.commit()
    return jsonify({'message': 'Movie deleted'})

if __name__ == '__main__':
    app.run(debug=True)
