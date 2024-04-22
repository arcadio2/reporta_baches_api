import jwt, datetime
from rest_framework.exceptions import AuthenticationFailed


def token_required(view_func):
    def wrapper(request, *args, **kwargs):
        authorization_header = request.META.get('HTTP_AUTHORIZATION', '')
        token = None
       
        if authorization_header.startswith('Bearer '):
            token = authorization_header[7:]

        if not token:
            token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated")

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated")
        
        return view_func(request, payload, *args, **kwargs)

    return wrapper