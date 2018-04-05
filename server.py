"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Movie, Rating, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = 'ABC123'

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


# =============================================================================
# Homepage

@app.route('/')
def index():
    """Homepage."""

    return render_template('homepage.html')

# =============================================================================
# Users


@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template('user_list.html', users=users)


@app.route('/users/<user_id>')
def user_page(user_id):
    """ Show user profile """

    user = User.query.filter_by(user_id=user_id).options(
        db.joinedload('ratings')).one()
    return render_template('user.html', user=user)

# =============================================================================
# Movies


@app.route('/movies')
def movie_list():
    """Show movie list"""

    movies = Movie.query.order_by(Movie.title).all()
    return render_template('movie_list.html', movies=movies)


@app.route('/movies/<movie_id>')
def movie_page(movie_id):
    """ Show movie details """

    movie = Movie.query.filter_by(movie_id=movie_id).options(
        db.joinedload('ratings')).one()

    prediction = None

    if 'email' in session:
        user = User.query.filter_by(email=session['email']).one()
        rating = Rating.query.filter_by(user_id=user.user_id,
                                        movie_id=movie_id).first()
        if rating is None:
            prediction = user.predict_rating(movie)
    else:
        rating = None

    return render_template('movie.html', movie=movie, rating=rating,
                           prediction=prediction)

# =============================================================================
# Ratings


@app.route('/add-rating/<movie_id>', methods=['POST'])
def add_rating(movie_id):
    """ Add new rating"""

    score = request.form.get('rating')
    user = User.query.filter_by(email=session['email']).one()
    rating = Rating.query.filter_by(user_id=user.user_id,
                                    movie_id=movie_id).first()

    if rating is None:
        rating = Rating(score=score, user_id=user.user_id, movie_id=movie_id)
        db.session.add(rating)
        flash('Rating Added')
    else:
        rating.score = score
        flash('Rating Updated')

    db.session.commit()

    return redirect('/movies/{}'.format(movie_id))

# =============================================================================
# Registration


@app.route('/register', methods=['GET'])
def register_form():
    """User creation form"""

    return render_template('register_form.html')


@app.route('/register', methods=['POST'])
def register_process():
    """User intake"""

    email = request.form.get('email')
    password = request.form.get('password')
    age = int(request.form.get('age'))
    zipcode = request.form.get('zipcode')

    if User.query.filter(User.email == email).first() is None:
        user = User(email=email, password=password, age=age, zipcode=zipcode)
        db.session.add(user)
        db.session.commit()
        session['email'] = email
        flash('User created and logged in')
        return redirect('/users/{}'.format(user.user_id))

    flash('User already exists')
    return redirect('/login')

# =============================================================================
# Login / Logout


@app.route('/login', methods=['GET'])
def login_form():
    """Display login form"""

    if 'email' in session:
        del session['email']

    return render_template('login_form.html')


@app.route('/login', methods=['POST'])
def login_process():
    """Log in user"""

    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()
    if user is None:
        flash('User not found')
        return redirect('/login')

    if password == user.password:
        session['email'] = email
        flash('Logged in as {}'.format(email))
        return redirect('/users/{}'.format(user.user_id))

    flash('Invalid password')
    return redirect('/login')


@app.route('/logout')
def logout_process():
    """Log out user"""

    if 'email' in session:
        del session['email']
        flash("Logged out")

    return redirect('/')

# =============================================================================
# Update User Info


@app.route('/update-user', methods=['GET'])
def update_form():
    """Show Update User Form"""

    return render_template('update_form.html')


@app.route('/update-user', methods=['POST'])
def update_process():
    """Update user details"""

    email = request.form.get('email')
    password = request.form.get('password')
    age = request.form.get('age')
    zipcode = request.form.get('zipcode')

    user = User.query.filter_by(email=session['email']).one()

    if email != '':
        user.email = email
        session['email'] = email
    if password != '':
        user.password = password
    if age != '':
        user.age = age
    if zipcode != '':
        user.zipcode = zipcode

    db.session.commit()

    flash('User info updated')

    return redirect('/users/{}'.format(user.user_id))


if __name__ == '__main__':
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    app.run(port=5000, host='0.0.0.0')
