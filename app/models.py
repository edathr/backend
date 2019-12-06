from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

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



class OldReview(db.Model):
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


    @classmethod
    def find_by_asin(cls, asin):
        return cls.query.filter_by(asin=asin).all()


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

    @classmethod
    def get_sum_count_rating(cls, asin):

        res = cls.query.filter_by(asin=asin)
        if res.count == 0:
            return 0, 0

        sum_rating = sum([e.review_rating for e in res])
        count_rating = res.count()

        return sum_rating, count_rating


class LiveReview(db.Model):
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

    @classmethod
    def get_sum_count_rating(cls, asin):

        res = cls.query.filter_by(asin=asin)
        if res.count() == 0:
            return 0, 0

        sum_rating = sum([e.review_rating for e in res])
        count_rating = res.count()

        return sum_rating, count_rating

    def serialize(self):
        books = mongo.db.kindle_metadata2
        print(self.asin)

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
    def find_by_asin(cls, asin):
        return cls.query.filter_by(asin=asin).all()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).all()

    @classmethod
    def find_by_asin_username(cls, asin, username):
        return cls.query.filter_by(asin=asin, username=username).first()

    @classmethod
    def patch_update(cls, asin, username, update_payload):
        print("patch_update", update_payload)
        review = cls.query.filter_by(asin=asin, username=username).first()
        if review == None:
            raise Exception("Asin and/or username is invalid")
        updated_review = review.update(update_payload)

        # print(review.serialize())
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

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def delete_from_db(cls, asin, username):
        if Favourite.query.filter_by(asin=asin, username=username).count() == 0:
            return False
        Favourite.query.filter_by(asin=asin, username=username).delete()
        db.session.commit()
        return True