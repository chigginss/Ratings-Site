"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64))
    password = db.Column(db.String(64))
    age = db.Column(db.Integer)
    zipcode = db.Column(db.String(15))

    def __repr__(self):
        """Representation of User instance"""

        return """\
<User: user_id={user_id}, email={email}, password={password}, age={age}, \
zipcode={zipcode}>""".format(user_id=user_id, email=email, password=password,
                             age=age, zipcode=zipcode)


class Movie(db.Model):
    """Movie object"""
    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(512), nullable=False)
    released_at = db.Column(db.DateTime, nullable=False)
    imbd_url = db.Column(db.String(256))

    def __repr__(self):
        """Representation of Movie instance"""

        return """\
<Movie: movie_id={movie_id}, title={title}, released_at={released_at}, \
imbd_url={imbd_url}>""".format(movie_id=movie_id, title=title,
                               released_at=released_at, imbd_url=imbd_url)


class Rating(db.Model):
    """ Rating object """

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        """Representation of User instance"""

        return """\
<Rating: rating_id={rating_id}, movie_id={movie_id}, user_id={user_id}, \
score={score}>""".format(rating_id=rating_id, movie_id=movie_id,
                         user_id=user_id, score=score)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
