

from functools import wraps


import jwt
from datetime import datetime, timezone, timedelta
from flask import request

from ...configurations.api.config import BaseConfig, SourceConfig



def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if "authorization" in request.headers:
            token = request.headers["authorization"]
        if not token:
            return {"success": False, "msg": "Valid JWT token is missing"}, 400

        try:

            data = JWTAuthentication().decode(token)
            current_user = {"email": data["email"], "_id": data['_id']}

        except jwt.ExpiredSignatureError:
            return {"success": False, "msg": "Token expired"}, 400
        except jwt.InvalidTokenError:
            return {"success": False, "msg": "Invalid token"}, 400

        return f(current_user, *args, **kwargs)

    return decorator

class JWTAuthentication:
    def __init__(self):
        self.key=BaseConfig.SECRET_KEY
        self.algorithm = BaseConfig.HASH_ALGORITHM
        self.default_expiry_minutes = 300
    def encode(self,email,user_id,expiry_in_minutes=None):
        if expiry_in_minutes is None:
            expiry = self.default_expiry_minutes
        else:
            expiry = expiry_in_minutes
        token=jwt.encode(
            {'email': email, '_id': user_id, 'exp': datetime.utcnow() + timedelta(minutes=expiry)},
            self.key
        )
        return token
    def decode(self,token):
        data=jwt.decode(token, self.key, algorithms=[self.algorithm])
        return data