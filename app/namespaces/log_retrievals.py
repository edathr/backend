from flask import jsonify
from flask_restplus import Resource, Namespace, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import mongo

logs = mongo.db.endpoint_logs

api = Namespace('logs', description='HTTP Logs Resource')  

http_logs_getter = reqparse.RequestParser()
http_logs_getter.add_argument('pg-size', default=10, help='Number of results returned each http call',
                                required=False)
http_logs_getter.add_argument('pg-num', default=1, help='Page Number starts from 1',
                                required=False)
http_logs_getter.add_argument('session_id', default='', help='session id',
                                required=False)
http_logs_getter.add_argument('user_id', default='', help='user id is the JWT token',
                                required=False)
http_logs_getter.add_argument('end_point', default=None, help='Example /books/',
                                required=False)
http_logs_getter.add_argument('request_type', default='', help='POST or GET or PATCH',
                                required=False)
http_logs_getter.add_argument('status', default='', help='Status code. Example: 404, 200',
                                required=False)
http_logs_getter.add_argument('filter', default='', help='filter options: session_id || user_id || end_point || request_type || status',
                                required=False)   

http_logs_helper = reqparse.RequestParser()
http_logs_helper.add_argument('limit', default=10, help='limit number of search recommenders',
                                required=False)
http_logs_helper.add_argument('filter', default='', help='filter options: session_id || user_id || end_point || request_type || status',
                                required=False)  
http_logs_helper.add_argument('prefix', default='', help='session id',
                                required=False)


@api.route('')
class HttpLogs(Resource):
    # We will sort via the ID. The request parser determines our query parameters
    @api.expect(http_logs_getter, Validate=True)
    @jwt_required
    def get(self):
        """
        Seach logs based on specified filter. If no filter given, fetch all. JWT required in Headers {Authorization: Bearer <JWT>}
        if given filter: return specified field which is either session_id || user_id || end_point || request_type || status
        If given session_id: return specific session details
        If given user_id: return specific user details
        If given end_point: return specific end point details
        If given request_type: return all requests of this type
        If given status: return specific status
        """
        data = http_logs_getter.parse_args()

        pg_size, pg_num = int(data["pg-size"]), int(data["pg-num"])
        start = (pg_num - 1) * pg_size
        end = start + pg_size
        filter_value = data.filter
        switcher = { 
            'session_id': data.session_id, 
            'user_id': data.user_id, 
            'end_point': data.end_point, 
            'request_type': data.request_type,
            'status': data.status,
            '': ''
        }
        filter_specific = switcher.get(filter_value, lambda: "Invalid filter")

        if filter_value == '':
            log_data = list(logs.find({}, {'raw': 0}))
        else:
            log_data = list(logs.find({filter_value: filter_specific}, {'raw': 0}))
        log_data.reverse()
        if log_data == []:
            return jsonify(data=dict(
                total_count=0,
                logs=[]))
        if start > len(log_data) - 1:
            return jsonify(data=dict(
                total_count=len(log_data),
                logs=[]))
        if end > len(log_data) - 1:
            return jsonify(data= dict(
                total_count = len(log_data),
                logs = log_data[start:]))
        return jsonify(data= dict(
            total_count = len(log_data),
            logs = log_data[start: end]))


@api.route('/autocomplete')
class HttpLogsHelper(Resource):
    @api.expect(http_logs_helper, Validate=True)
    @jwt_required
    def get(self):
        """
        Autocomplete for possible values to type in the search bar. defaults to user_id. JWT required in Headers {Authorization: Bearer <JWT>}
        if given filter: return specified field which is either session_id || user_id || end_point || request_type || status
        If given limit: Number of searches to limit to 
        If given prefix: Autocomplete is case-insensitive
        """
        data = http_logs_helper.parse_args()
        filter_value = data.filter
        if filter_value == '':
            log_data = list(logs.distinct('user_id'))
        else:
            log_data = list(logs.distinct(filter_value))
        if data.prefix != '':
            prefix = data.prefix
            log_data = list(filter(lambda x: prefix in x, log_data)) 
        return jsonify(data= dict(
            total_count = len(log_data),
            logs_search = log_data[:int(data.limit)]),
            )