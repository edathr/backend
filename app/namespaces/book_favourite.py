from flask_restplus import Resource, Namespace, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, LiveReview, OldReview, Favourite

api = Namespace('books/favourite', description='Books Favourite Resource')

# ---POST-----
book_favourite_parser = reqparse.RequestParser()
book_favourite_parser.add_argument('book_asin', help='Asin field of book cannot be blank',
                                   required=True)

# ---PATCH-----
patch_book_favourite_parser = reqparse.RequestParser()
patch_book_favourite_parser.add_argument('book_asin', help='Asin field of book cannot be blank',
                                   required=True)


@api.route('/')
class BookFavourite(Resource):

    @api.expect(book_favourite_parser, Validate=True)
    @jwt_required
    def post(self):
        """JWT required in Headers {Authorization: Bearer <JWT>}. Create a book review identifed by its asin. e.g. B000FA64PK"""
        jwt_username = get_jwt_identity()
        data = book_favourite_parser.parse_args()
        book_asin = data["book_asin"]

        favourite_record = Favourite(asin=book_asin, username=jwt_username)

        try:
            favourite_record.save_to_db()

            return {"data": f"Book {book_asin} has been successfully favourited"}, 201


        except Exception as e:
            print(str(e))
            return {
                       "data": {
                           "message": "This book has already been favourited by the user",
                           "details": str(e)
                       }
                   }, 403


    @api.expect(patch_book_favourite_parser, Validate=True)
    @jwt_required
    def delete(self):
        "JWT required in Headers {Authorization: Bearer <JWT>}. Unfavourite a book, deletes a favourite book record."
        jwt_username = get_jwt_identity()
        data = patch_book_favourite_parser.parse_args()
        book_asin = data["book_asin"]

        try:
            if Favourite.delete_from_db(asin=book_asin, username=jwt_username):

                return {
                    "data": {
                        "message": f"Book {book_asin} has been successfully UN-favourited"}
                    },200

            else:
                return {
                           "data": {
                               "message": f"Book {book_asin} favourite record for user not found"}
                       }, 404



        except Exception as e:
            return {
                       "data": {
                           "message": "To be confirmed",
                           "details": str(e)
                       }
                   }, 403




