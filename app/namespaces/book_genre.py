from flask import jsonify
from flask_restplus import Resource, Namespace, reqparse
from .genres import STATIC_GENRES
from .. import mongo
from .lib import sanitize

api = Namespace('books/genres', description='Get top 500 genres + Get books that match a certain genre')

# ---GET-----
book_by_genre = reqparse.RequestParser()
book_by_genre.add_argument('pg-size', default=10, help='Number of results returned each http call',
                                required=False)
book_by_genre.add_argument('pg-num', default=1, help='Page Number starts from 1',
                                required=False)


books = mongo.db.kindle_metadata2

@api.route('')
class Genre(Resource):

    def get(self):
        """Return top 500 genres. These 500 genres are not exahustive. There are 4000 genres in total,
        that we will still support when the user is querying a genre not in the top 496.
        Return type: { num_genres: x, data: { genre1: count1, genre2: count2} }"""


        return dict(
            num_genres = len(STATIC_GENRES),
            data = STATIC_GENRES)


@api.route('/<string:genre>')
class BookByGenre(Resource):

    @api.expect(book_by_genre, Validate=True)
    def get(self, genre):
        """Books based on the genre. If no books match the genre, return 404"""

        params = book_by_genre.parse_args()
        pg_size, pg_num = int(params["pg-size"]), int(params["pg-num"])
        start = (pg_num - 1) * pg_size
        end = start + pg_size
        books_data = books.find({"genres": {"$in": [genre]}}).skip(start).limit(end-start)
        book_count = books_data.count()

        if book_count == 0:
            return dict(data = None), 404

        book_data_list = list(books_data)
        for i in range(len(book_data_list)):
            book_data_list[i] = sanitize(book_data_list[i])

        return jsonify(data= dict(
            num_books = book_count,
            books = book_data_list))