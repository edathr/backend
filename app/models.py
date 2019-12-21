from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

def sanitize_short(e):
    if not e.get("author", None):
        e["author"] = "Author not found"

    if not e.get("title", None):
        e["title"] = "Title not found"

    return e

def get_average_rating(asin):
    """Get avg_rating from SQL as the source of truth"""

    old_sum, old_count = OldReview.get_sum_count_rating(asin)
    new_sum, new_count = LiveReview.get_sum_count_rating(asin)

    if old_count + new_count == 0:
        return 0

    return round((old_sum + new_sum) / (old_count + new_count), 1)



db = SQLAlchemy()
from . import mongo

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(120), nullable=False)

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @property
    def password(self):
        """
        Prevent pasword from being accessed
        """
        raise AttributeError('password is not a readable attribute.')

    @staticmethod
    def hash_password(password):
        """
        Set password to a hashed password
        """
        return generate_password_hash(password)

    @staticmethod
    def verify_password(password_hash, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(password_hash, password)

    def __repr__(self):

        return f"User: {self.username}"


class RevokedTokenModel(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)


class Review:

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).all()

    @classmethod
    def find_reviews_for_user(cls, username):
        books = mongo.db.kindle_metadata2
        reviews = list(cls.query.filter_by(username=username))
        print("reviews", reviews)

        # if len(reviews) == 0:
        #     return []

        review_books = []

        for e in reviews:
            new_e = books.find_one({"asin": e.asin}, {"imUrl": 1, "title": 1, "author": 1, "_id": 0})

            try:
                new_e["asin"] = e.asin
                new_e["user_rating"] = e.review_rating
                new_e["avg_rating"] = get_average_rating(e.asin)
                new_e = sanitize_short(new_e)

                review_books.append(new_e)

            except:
                continue

        return review_books


    @classmethod
    def find_num_review_for_user(cls, username):
        return cls.query.filter_by(username=username).count()

    @classmethod
    def find_avg_rating_user(cls, username):

        ratings = list(cls.query.filter_by(username=username))
        if len(ratings) == 0:
            return 0
        return round(sum([e.review_rating for e in ratings]) / len(ratings), 2)

    @classmethod
    def find_by_asin(cls, asin):
        return cls.query.filter_by(asin=asin).all()

    @classmethod
    def user_exists(cls, username):
        if cls.query.filter_by(username=username).count() == 0:
            return False

        else:
            return True

    @classmethod
    def get_sum_count_rating(cls, asin):

        res = cls.query.filter_by(asin=asin)
        if res.count == 0:
            return 0, 0

        sum_rating = sum([e.review_rating for e in res])
        count_rating = res.count()

        return sum_rating, count_rating

    @classmethod
    def find_by_asin_username(cls, asin, username):
        return cls.query.filter_by(asin=asin, username=username).first()



class OldReview(db.Model, Review):
    __tablename__ = 'historical_reviews'
    id = db.Column(db.Integer, primary_key=True)
    asin = db.Column(db.String(20), nullable=False, index=True)
    helpful_rating = db.Column(db.Integer)
    total_helpful_rating = db.Column(db.Integer)
    review_rating = db.Column(db.Integer)
    review_text = db.Column(db.TEXT)
    summary_text = db.Column(db.String(15000))
    username = db.Column(db.String(200))
    reviewer_id = db.Column(db.String(200))
    date_time = db.Column(db.DateTime())
    unix_timestamp = db.Column(db.Integer, nullable=False)



    def serialize(self):
        books = mongo.db.kindle_metadata2
        imUrl = books.find_one({"asin": self.asin}, {"imUrl": 1})["imUrl"]
        return dict(
            id = self.id,
            asin = self.asin,
            helpful = self.helpful_rating,
            total_helpful = self.total_helpful_rating,
            review_rating = self.review_rating,
            review_text = self.review_text,
            username=self.username,
            summary_text = self.summary_text,
            # reviewer_id = self.reviewer_id,
            # date_time = self.date_time,
            unix_timestamp = self.unix_timestamp,
            old_review = True,
            imUrl = imUrl

        )




class LiveReview(db.Model, Review):
    __tablename__ = 'live_reviews'
    __table_args__ = (
        db.UniqueConstraint('asin', 'username', name='asin_username_constraint'),
    )
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), db.ForeignKey('users.username'))
    asin = db.Column(db.String(20), nullable=False)
    review_rating = db.Column(db.FLOAT)
    review_text = db.Column(db.TEXT)
    unix_timestamp = db.Column(db.Integer, nullable=False)



    def serialize(self):
        books = mongo.db.kindle_metadata2

        try:
            imUrl = books.find_one({"asin": self.asin}, {"imUrl": 1})["imUrl"]

        except:
            imUrl = None

        return dict(
            id = self.id,
            asin = self.asin,
            review_rating = self.review_rating,
            review_text = self.review_text,
            username = self.username,
            unix_timestamp = self.unix_timestamp,
            old_review =False,
            imUrl = imUrl,

            # TODO: Fix this
            title="Title not found"

        )

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


    def update(self, update_payload):
        for k,v in update_payload.items():
            self.__setattr__(k, v)

        return self


    @classmethod
    def patch_update(cls, asin, username, update_payload):
        print("patch_update", update_payload)
        review = cls.query.filter_by(asin=asin, username=username).first()
        if review == None:
            raise Exception("Asin and/or username is invalid")
        updated_review = review.update(update_payload)

        db.session.commit()
        return updated_review.serialize()


class Favourite(db.Model):
    __tablename__ = 'favourites'
    __table_args__ = (
        db.UniqueConstraint('asin', 'username', name='asin_username_constraint'),
    )
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), db.ForeignKey('users.username'))
    asin = db.Column(db.String(20), nullable=False)

    @classmethod
    def find_favourites_for_user(cls, username):
        books = mongo.db.kindle_metadata2
        favourites = list(cls.query.filter_by(username=username))
        favourite_books = []

        for e in favourites:
            new_e = books.find_one({"asin": e.asin}, {"imUrl": 1, "title": 1, "author": 1, "_id": 0})

            try:
                new_e["asin"] = e.asin
                new_e["avg_rating"] = get_average_rating(e.asin)
                new_e = sanitize_short(new_e)
                favourite_books.append(new_e)

            except:

                new_e = {
      "imUrl": "imgUrl not found",
      "asin": e.asin,
      "avg_rating": -1,
      "author": "Author not found",
      "title": "Title not found"
    }
                favourite_books.append(new_e)
                continue

        return favourite_books


    def serialize(self):

        return dict(
            id = self.id,
            username = self.username,
            asin = self.asin
        )

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def delete_from_db(cls, asin, username):
        if not Favourite.find_user_asin(asin, username):
            return False
        Favourite.query.filter_by(asin=asin, username=username).delete()
        db.session.commit()
        return True


    @classmethod
    def find_user_asin(cls, asin, username):
        if Favourite.query.filter_by(asin=asin, username=username).count() == 0:
            return False

        return True


    @classmethod
    def num_favourite(cls, asin):
        return Favourite.query.filter_by(asin=asin).count()

    @classmethod
    def num_favourite_by_user(cls, username):
        return Favourite.query.filter_by(username=username).count()