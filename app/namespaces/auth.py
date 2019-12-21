from flask import Flask, jsonify, current_app
from flask_restplus import Api, Resource, reqparse, Namespace
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_raw_jwt, JWTManager
from .. import jwt
import copy


api = Namespace('auth', description="Authentication Resource")

register_credentials = reqparse.RequestParser()
register_credentials.add_argument('username', default="tester", help='Username field cannot be blank',
                                  required=True)

register_credentials.add_argument('password', default="pleasedDoNotHack", help='Password field cannot be blank',
                                  required=True)
login_credentials = copy.deepcopy(register_credentials)
register_credentials.add_argument('email', default="test@example.com", help='Email field cannot be blank',
                                  required=True)


from ..models import User, RevokedTokenModel, OldReview

@api.route('/register')
class UserRegistration(Resource):

    @api.expect(register_credentials, Validate=True)
    def post(self):

        data = register_credentials.parse_args()

        # TODO: fix this part
        # Do not allow username conflict with historical reviews database
        # if OldReview.user_exists(data["username"]):
        #     return {"data":
        #                 {'message': f"Username exists inside our historical reviews database. We do not allow a collision. I am sorry."}
        #             }, 403

        new_user = User(

            email=data['email'],
            username=data['username'],
            password_hash=User.hash_password(data["password"])
        )

        try:
            new_user.save_to_db()
            access_token = create_access_token(identity=data['username'])

            return {
                       "data": {
                           "username": new_user.username,
                           'access_token': access_token
                       }

                   }, 201
        except Exception as e:
            print(str(e))
            return {}, 403


@api.route('/login')
@api.expect(login_credentials, Validate=True)
class UserLogin(Resource):
    def post(self):

        data = login_credentials.parse_args()
        current_user = User.find_by_username(data['username'])

        if not current_user:
            return {"data":
                        {'message': f"User {data['username']} not found"}
                    }, 404

        if User.verify_password(current_user.password_hash, data['password']):
            access_token = create_access_token(identity=data['username'])

            return {
                       "data": {
                           "username": current_user.username,
                           'access_token': access_token
                       }

                   }, 200
        else:
            return {
                       "data": {
                           "message": "Wrong credentials"
                       }
                   }, 500

    @api.route('/logout')
    class UserLogoutAccess(Resource):
        """
        Put the JWT in the header in the following format

        Authorization: Bearer <JWT>

        """

        @jwt_required
        def post(self):
            jti = get_raw_jwt()['jti']
            try:
                revoked_token = RevokedTokenModel(jti=jti)
                revoked_token.add()
                return {
                           "data": {'message': 'Access token has been revoked'}
                       }, 200
            except:
                return {
                           "data": {
                               'message': 'Something went wrong',
                           }
                       }, 500

    @api.route('/test')
    class TestAuthManually(Resource):
        """Test if you have the access token in your header"""
        @jwt_required
        @jwt.token_in_blacklist_loader
        def get(self):
            return jsonify(data="Get request successful. You have been authenticated"), 200

        @jwt_required
        @jwt.token_in_blacklist_loader
        def post(self):
            return jsonify(data="Post request successful. You have been authenticated"), 200

