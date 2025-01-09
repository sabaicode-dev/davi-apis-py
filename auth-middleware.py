from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import jwt

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization')
        if not token:
            return None  # No token provided

        try:
            # Decode JWT
            payload = jwt.decode(token, 'your-secret-key', algorithms=['HS256'])
            user_cognito_id = payload.get('user_id')  # Extract cognitoUserId
            if not user_cognito_id:
                raise AuthenticationFailed('Invalid token')

            return (user_cognito_id, None)  # Attach cognitoUserId to request.user
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
