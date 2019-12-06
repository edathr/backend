from flask_restplus import Namespace, Resource
from flask import jsonify
import re

api = Namespace('books/search', description='Books Search Resource')

from .. import mongo
from .lib import sanitize, PROJECTION

books = mongo.db.kindle_metadata2

@api.route('/autocomplete/<string:prefix>')
@api.route('/autocomplete/<string:prefix>/<int:limit>')
class BookAutocomplete(Resource):

    def get(self, prefix, limit=50):
        """Autocomplete with case-insensitive, each word matching for book search. Limit=50 by default.
        Limit is an optional url parameter."""

        regx = re.compile("^{}".format(prefix), re.IGNORECASE)

        book_data = list(books.find({"$or": [{"$text": {"$search": prefix}}, {"title": regx}]},
                               {"asin": 1, "title": 1, "imUrl": 1}, limit=limit))

        for i in range(len(book_data)):
            book_data[i] = sanitize(book_data[i])



        return jsonify(data=book_data)


@api.route('/<string:query>')
class BookSearch(Resource):

    def get(self, query):
        """Search database for book titles. Limit is 50"""

        book_data = list(books.find({"$text": {"$search": query}}, limit=50))

        for i in range(len(book_data)):
            book_data[i] = sanitize(book_data[i])


        return jsonify(data=book_data)


class BookBestSellers(Resource):
    def get(self, username):
        """Get a list of 10 top recommended books for a particular user"""
        if username == "":
            output = dict(status_code=400, reason="Username should not be empty")
            return jsonify(data=output)

        # random placeholder function
        start = 0
        for c in username:
            start += ord(c)

        data = list(books.find({}, PROJECTION)[start: start + 10])

        return jsonify(data=data)