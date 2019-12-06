from flask import jsonify
from flask_restplus import Resource, Namespace, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import mongo
import requests
from .lib import parse_gbook
from datetime import datetime
from pytz import timezone

books = mongo.db.kindle_metadata2

api = Namespace('books/add', description='Add books based on title and author by leveraging Google API')

# ---GET-----
find_book_parser = reqparse.RequestParser()
find_book_parser.add_argument('title', default="Harry Potter and the Goblet of Fire", help='Title Field cannot be blank',
                              required=True)

find_book_parser.add_argument('author', default=None,
                              help='Author Field is optional',
                              required=False)
# ----POST------
add_book_parser = reqparse.RequestParser()
add_book_parser.add_argument('asin', default = None,
                             help= "asin Field is required", required = True)

add_book_parser.add_argument('title', default = None,
                             help= "title Field is required", required = True)

parse_fields = ["author", "description", "genres", "imUrl"]

for field_name in parse_fields:
    add_book_parser.add_argument(field_name, default=None,
                                 help=f"{field_name} Field is required", required=True)

# ------GET-------
get_book_parser = reqparse.RequestParser()
get_book_parser.add_argument('pg-size', default=10, help='Number of results returned each http call',
                                required=False)
get_book_parser.add_argument('pg-num', default=1, help='Page Number starts from 1',
                                required=False)

API_KEY = "AIzaSyA68wWrXPVtGdVy4APQRZGJTHE_mo8b_Pk"

@api.route('/search')
class NewBook(Resource):
    @jwt_required
    @api.expect(find_book_parser, Validate=True)
    def get(self):
        """JWT required in Headers {Authorization: Bearer <JWT>}. Search a book on google api based on title and author (optional) """
        jwt_username = get_jwt_identity()
        data = find_book_parser.parse_args()
        title = data["title"]
        author = data["author"]
        print("author", author)

        if not author:
            URL = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title}&key={API_KEY}"

        else:
            URL = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title}+inauthor:{author}&key={API_KEY}"

        res_obj = requests.get(URL)

        try:
            book_data = res_obj.json()["items"]

        except KeyError:
            return {}, 404

        if res_obj.status_code == 200:
            if len(book_data) >= 3:
                results = book_data[:3]
            else:
                results = book_data

            book_data = [parse_gbook(e) for e in results]

            return jsonify(data=book_data)


        else:
            return {}, res_obj.status_code


@api.route('')
class NewBook(Resource):
    @jwt_required
    @api.expect(add_book_parser, Validate=True)
    def post(self):
        """Make sure to pass unexpired JWT Token in Headers"""

        new_book_data = add_book_parser.parse_args()
        if len(list(books.find({"asin": new_book_data["asin"]}))):
            return {"message": "book already exists in database"}, 403

        else:
            new_book_data["newly_added"] = 1
            new_book_data["added_by"] = get_jwt_identity()
            time_now = datetime.now(timezone("Singapore"))
            new_book_data["time_added"] = time_now.strftime("%d/%m/%Y %H:%M:%S")
            books.insert(new_book_data)

            return {"message": "New book successfully added"}, 201




@api.route('/history')
class NewBook(Resource):
    @jwt_required
    @api.expect(get_book_parser, Validate=True)
    def get(self):
        """Make sure to pass unexpired JWT Token in Headers"""
        params = get_book_parser.parse_args()
        pg_size, pg_num = int(params["pg-size"]), int(params["pg-num"])
        start = (pg_num - 1) * pg_size
        end = start + pg_size
        books_data = books.find({"newly_added": 1}).skip(start).limit(end - start).sort([("_id", -1)])

        book_count = books_data.count()

        if book_count == 0:
            return dict(data=None), 404

        book_data_list = list(books_data)

        return jsonify(data=dict(
            num_books=book_count,
            books=book_data_list))
