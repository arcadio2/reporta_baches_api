import jwt, datetime
from rest_framework.exceptions import AuthenticationFailed


def validate_token(request):
    authorization_header = request.META.get('HTTP_AUTHORIZATION', '')
    
    token=None
    # Verificar si el encabezado de autorización comienza con "Bearer "
    if authorization_header.startswith('Bearer '):
    # Extraer el token eliminando el prefijo "Bearer jwt="
        token = authorization_header[11:]

    #valida si no existe token
    if(not token):
        #sino existe puede venir de las cookies
        token = request.COOKIES.get('jwt')

    #si tampoco existe en las cookies, entonces mandamos error
    if(not token):
        raise AuthenticationFailed("Unathenticated")
    
    #Decodificamos el token
    try:
        payload = jwt.decode(token,'secret',algorithms=['HS256'])

    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Unauthenticated")
    
    return payload