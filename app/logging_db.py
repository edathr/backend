import logging
from datetime import datetime, timedelta
import time
import re
import jwt

class LogMongoHandler(logging.Handler):
    def __init__(self, db_connection, request):
        logging.Handler.__init__(self)
        self.db_connection = db_connection
        self.session_id = ''
        self.user_id = ''
        if 'X-Client-ID' in request.headers:
            self.session_id = request.headers['X-Client-ID']
        if 'Authorization' in request.headers:
            filtered = re.findall("Bearer (\w.+)", request.headers['Authorization'])[0]
            payload = jwt.decode(filtered, "thisisnottherealsecretkeydumbass")
            self.user_id = payload['identity']
        self.request_body = request.get_data()

    def emit(self, record):
        # Set current time
        # tm = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))
        tm = datetime.now()+ timedelta(hours=8)
        tm = str(tm).split('.')[0]
        # Acccess the message from flask
        self.log_msg = record.msg
        self.status = ''
        self.ip = ''
        self.end_point = ''
        self.request_type = ''
        try:
            status = re.findall("\" ([0-9]+) -", record.msg)
            if status != []:
                self.status = status[0]                
            ip = re.findall("[0-9.]+", record.msg)
            if ip != []:
                self.ip = ip[0]
            request_type = re.findall('\"([a-zA-Z]+)',record.msg)
            if request_type != []:
                self.request_type = request_type[0]
            end_point = re.findall(' ([/a-zA-Z]+(/)?)',record.msg)
            if end_point != []:
                self.end_point = end_point[0][0]
        except Exception as e:
            print(e)
        # Check for health check, swagger ui and docs in logging
        banned_endpoints = ['/swaggerui/', '', '/docs/', '/swaggerui/favicon', '/swagger', '/swaggerui/swagger', '/swaggerui/droid']
        if self.end_point not in banned_endpoints:
            try:
                self.db_connection.insert( { 
                    "body": str(self.request_body),
                    "session_id": self.session_id,
                    "user_id": self.user_id,
                    "raw": self.log_msg,
                    "ip": self.ip,
                    "end_point": self.end_point,
                    "request_type": self.request_type,
                    "status": self.status,
                    "time": str(tm),
                } )
            except Exception as e:
                print(e)