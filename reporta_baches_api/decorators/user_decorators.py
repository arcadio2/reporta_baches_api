import jwt, datetime
from rest_framework.exceptions import AuthenticationFailed


def token_required(view_func):
    def wrapper(request, *args, **kwargs):
        authorization_header = request.META.get('HTTP_AUTHORIZATION', '')
        print(authorization_header)
        token = None
       
        if authorization_header.startswith('Bearer '):
            token = authorization_header[7:]

        if not token:
            token = request.COOKIES.get('jwt')

        print(token)

        if not token:
            raise AuthenticationFailed("Unauthenticated")

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            print(payload)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated")
        
        return view_func(request, payload, *args, **kwargs)

    return wrapper