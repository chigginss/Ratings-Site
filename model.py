"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy
import correlation

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

    ratings = db.relationship('Rating')

    def __repr__(self):
        """Representation of User instance"""

        return "<User: user_id={}, email={}>".format(self.user_id, self.email)

    def similarity(self, other, print_list=False):
        """Find similatiry between two users"""

        u_ratings = {}
        paired_ratings = []

        for u_rating in self.ratings:
            u_ratings[u_rating.movie_id] = u_rating

        for o_rating in other.ratings:
            u_rating = u_ratings.get(o_rating.movie_id)
            if u_rating:
                paired_ratings.append((u_rating.score, o_rating.score))

        if print_list:
            print paired_ratings

        if paired_ratings:
            return correlation.pearson(paired_ratings)

        return 0.0

    def predict_rating(self, movie):
        """Predict users rating of movie"""

        other_users = sorted([(self.similarity(rating.user), rating)
                              for rating in movie.ratings])

        # best_match = other_users[-1]

        # print best_match[0], best_match[1].score, best_match[1].user
        # print self.similarity(best_match[1].user, print_list=True)

        # prediction = best_match[0] * best_match[1].score

        upper_bound = 1
        lower_bound = 0

        pos_list = [sim * rating.score for sim, rating in other_users
                    if upper_bound > sim > lower_bound]
        pos = sum(pos_list)

        neg_list = [-sim * abs(rating.score-6) for sim, rating in other_users
                    if -upper_bound < sim < -lower_bound]
        neg = sum(neg_list)

        denominator = sum([abs(sim) for sim, _ in other_users
                           if upper_bound > sim > lower_bound
                           or -upper_bound < sim < -lower_bound])

        print 'bounds', upper_bound, lower_bound
        print 'pos', len(pos_list), '-', pos
        print 'neg', len(neg_list), '-', neg
        print 'denom', denominator

        prediction = (pos + neg) / denominator

        return prediction


class Movie(db.Model):
    """Movie object"""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    released_at = db.Column(db.DateTime, nullable=False)
    imbd_url = db.Column(db.String(256))

    ratings = db.relationship('Rating')

    def __repr__(self):
        """Representation of Movie instance"""

        return "<Movie: movie_id={}, title={}>".format(self.movie_id,
                                                       self.title)


class Rating(db.Model):
    """ Rating object """

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'),
                         nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'),
                        nullable=False)
    score = db.Column(db.Integer, nullable=False)

    user = db.relationship('User')
    movie = db.relationship('Movie')

    def __repr__(self):
        """Representation of User instance"""

        return "<Rating: rating_id={}, movie_id={}, user_id={}, score={}>".format(
            self.rating_id, self.movie_id, self.user_id, self.score)


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
