from flask import jsonify
from flask_restplus import  Resource, Namespace
from .lib import sanitize, PROJECTION
from ..models import Favourite, OldReview, LiveReview, User

api = Namespace('user', description='Books Resource')
from .. import mongo

books = mongo.db.kindle_metadata2


@api.route('/<string:username>')
class UserPage(Resource):

    def get(self, username):
        """
        Based on the username, get all the details of the user
        """

        if OldReview.user_exists(username):
            cls = OldReview

        elif User.find_by_username(username) is None:
            return {"message": "User not found (both in historical review or live user database)"}, 404

        else:
            cls = LiveReview

        num_fav = Favourite.num_favourite_by_user(username)
        num_reviews = cls.find_num_review_for_user(username)

        books_reviewed = cls.find_reviews_for_user(username)
        books_favourite = Favourite.find_favourites_for_user(username)
        avg_rating = cls.find_avg_rating_user(username)

        return dict(
            username = username,
            num_reviews=num_reviews,
            avg_rating = avg_rating,
            num_fav = num_fav,
            books_reviewed = books_reviewed,
            books_favourite = books_favourite
                    )
