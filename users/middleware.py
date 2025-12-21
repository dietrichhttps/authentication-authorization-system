from django.utils.deprecation import MiddlewareMixin
from users.utils import get_user_from_token, get_user_from_session_token


class UserIdentificationMiddleware(MiddlewareMixin):
    """
    Middleware для идентификации пользователя из токена или сессии.
    Проверяет Authorization header (Bearer token) или cookie session_id
    """
    
    def process_request(self, request):
        # Сбрасываем request.user, чтобы использовать нашу систему
        request.user = None
        
        # Проверяем Authorization header (JWT токен)
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split('Bearer ')[1].strip()
            user = get_user_from_token(token)
            if user:
                request.user = user
                return None
        
        # Проверяем cookie с session_id
        session_token = request.COOKIES.get('session_id')
        if session_token:
            user = get_user_from_session_token(session_token)
            if user:
                request.user = user
        
        return None

