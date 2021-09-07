from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import Response

def roleDecorator(role):
    def innerRole(function):
        @wraps(function)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if "role" in claims and role == claims["role"]:
                return function(*args, **kwargs)
            else:
                return Response("Permission denied!", status = 403)
        return decorator
    return innerRole
