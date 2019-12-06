from flask import jsonify
from flask_restplus import Resource, Namespace, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
import time
from ..models import User, LiveReview, OldReview
from .. import mongo

api = Namespace('books/reviews', description='Books Review Resource')

# ---GET-----
book_review_getter = reqparse.RequestParser()
book_review_getter.add_argument('pg-size', default=10, help='Number of results returned each http call',
                                required=False)
book_review_getter.add_argument('pg-num', default=1, help='Page Number starts from 1',
                                required=False)

# ---POST-----
book_review_parser = reqparse.RequestParser()
book_review_parser.add_argument('review_rating', default="1", help='Rating field cannot be blank',
                                required=True)
book_review_parser.add_argument('review_text', default="I enjoyed this book a lot",
                                help='Review Text field cannot be blank',
                                required=True)

# ---PATCH-----

patch_book_review_parser = reqparse.RequestParser()
patch_book_review_parser.add_argument('review_rating', type=float, default="1", help='Rating field can be blank',
                                      required=False)
patch_book_review_parser.add_argument('review_text', default="I enjoyed this book a lot",
                                      help='Review Text field can be blank',
                                      required=False)


@api.route('/<string:asin>')
class BookReview(Resource):

    @api.expect(book_review_getter, Validate=True)
    def get(self, asin):
        """Returns new and old Reviews for the book given asin (B000FA64PK). New and old reviews are differentiated by their "old_review" field's value. Page Number starts from 1"""

        params = book_review_getter.parse_args()
        pg_size, pg_num = int(params["pg-size"]), int(params["pg-num"])
        start = (pg_num - 1) * pg_size
        end = start + pg_size

        new_records = LiveReview.find_by_asin(asin)
        old_records = OldReview.find_by_asin(asin)

        records = old_records + new_records

        if records == [] or start > len(records) - 1:
            return jsonify(data=dict(
                num_reviews=0,
                reviews=[]))

        reviews = [e.serialize() for e in records]
        reviews.reverse()

        # Return whatever is left if we overshoot
        if end > len(reviews) - 1:
            return jsonify(data=dict(
                num_reviews=len(reviews),
                reviews=reviews[start: end]))

        # TODO: Check if book exists, 404 if does not exist
        return jsonify(data=dict(
            num_reviews=len(reviews),
            reviews=reviews[start: end]))

    @api.expect(book_review_parser, Validate=True)
    @jwt_required
    def post(self, asin):
        """JWT required in Headers {Authorization: Bearer <JWT>}. Create a book review identifed by its asin. e.g. B000FA64PK"""
        jwt_username = get_jwt_identity()
        data = book_review_parser.parse_args()

        new_review = LiveReview(
            asin=asin,
            username=jwt_username,
            review_rating=data.review_rating,
            review_text=data.review_text,
            unix_timestamp=int(time.time())

        )


        try:
            new_review.save_to_db()

            return {"data": new_review.serialize()}, 201

        except Exception as e:
            print(str(e))
            return {
                       "data": {
                           "message": "This error is likely due to a user trying to post a second review for the same asin. Please use PATCH instead",
                           "details": str(e)
                       }
                   }, 403

    @api.expect(patch_book_review_parser, Validate=True)
    @jwt_required
    def patch(self, asin):
        """JWT required in Headers {Authorization: Bearer <JWT>}. All fields are optional except for asin. API will update the resource for all fields."""
        jwt_username = get_jwt_identity()
        data = patch_book_review_parser.parse_args()
        update_payload = {k: v for k, v in data.items() if v != ""}
        print("Update payload", update_payload)

        try:
            new_review = LiveReview.patch_update(asin, jwt_username, update_payload)


        except Exception as e:
            print(str(e))
            return {}, 403

        return {"data": new_review}, 200


@api.route('/user/<string:username>')
@api.expect(book_review_getter, Validate=True)
class UserBookReview(Resource):
    def get(self, username):
        """Returns all reviews from user"""
        num_reviews = 0

        params = book_review_getter.parse_args()
        pg_size, pg_num = int(params["pg-size"]), int(params["pg-num"])
        start = (pg_num - 1) * pg_size
        end = start + pg_size

        if not User.find_by_username(username):
            return {"data": {"message": "Username not found"}}, 404

        ret = LiveReview.find_by_username(username)
        output = [e.serialize() for e in ret]
        num_reviews = len(output)

        if ret == []:
            return jsonify(data=dict(num_reviews=num_reviews, reviews=[]))

        return jsonify(data=dict(num_reviews=num_reviews, reviews=output[start:end]))


@api.route('/user/<string:username>/<string:asin>')
class UserSpecificBookReview(Resource):
    def get(self, username, asin):
        """Returns reviews written by user for specific asin. e.g. B000FA64PK"""

        if not User.find_by_username(username):
            return {"data": {"message": "Username not found"}}, 404

        # TODO: check if book exists
        ret = LiveReview.find_by_asin_username(asin, username)

        if not ret:
            return {"data": {}}, 200

        output = ret.serialize()

        return jsonify(data=output)
