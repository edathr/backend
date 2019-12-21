from flask import jsonify
from flask_restplus import  Resource, Namespace
from flask_jwt_extended import jwt_optional, get_jwt_identity
from .lib import sanitize, PROJECTION
from ..models import Favourite

api = Namespace('books', description='Books Resource')
from .. import mongo

books = mongo.db.kindle_metadata2

@api.route('')
@api.route('/<string:asin>')
class BookList(Resource):
    @jwt_optional
    def get(self, asin=None, limit=100):

        """
        If given asin: return specific book eg B000FA64PK | If not given asin: Return number of books subjected to limit=100.
        """
        username = get_jwt_identity()
        if asin is None:
            book_data = list(books.find({}, limit =limit))

            for i in range(len(book_data)):
                book_data[i] = sanitize(book_data[i])

                return jsonify(data=book_data)
        else:
            # Book page
            book_data = list(books.find({"asin": asin},
                                        limit=1
                                        ))
            if len(book_data) == 1:
                e = sanitize(book_data[0])
                if not username:
                    e["user_fav"] = False

                else:

                    e["user_fav"] = Favourite.find_user_asin(asin=asin, username=username)

                e["num_fav"] = Favourite.num_favourite(asin=asin)
                return jsonify(data=e)

            else:
                return {"data": None}, 404





@api.route('/recommended/<string:username>')
class BookRecommendedList(Resource):
    def get(self, username):
        """Get a list of 10 top recommended books for a particular user"""
        if username == "":
            output = dict(status_code=400, reason="Username should not be empty")
            return jsonify(data=output)

        # TODO: Replace this random placeholder function for personalised recommendation
        start = 0
        for c in username:
            start += ord(c)

        start %= 90
        book_data = list(books.find({}, PROJECTION, limit=10))
        for i in range(len(book_data)):

            book_data[i] = sanitize(book_data[i])

        return jsonify(data=book_data)