import jwt
from datetime import datetime, timedelta
from django.conf import settings
from users.models import User, Session


def generate_jwt_token(user_id):
    """Генерирует JWT токен для пользователя"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7),  # Токен действует 7 дней
        'iat': datetime.utcnow(),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def decode_jwt_token(token):
    """Декодирует JWT токен и возвращает payload"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_user_from_token(token):
    """Получает пользователя по JWT токену"""
    payload = decode_jwt_token(token)
    if not payload:
        return None
    
    user_id = payload.get('user_id')
    if not user_id:
        return None
    
    try:
        user = User.objects.get(id=user_id, is_active=True)
        return user
    except User.DoesNotExist:
        return None


def create_session(user, token):
    """Создает сессию для пользователя"""
    expires_at = datetime.utcnow() + timedelta(days=7)
    session, created = Session.objects.get_or_create(
        user=user,
        session_token=token,
        defaults={'expires_at': expires_at}
    )
    if not created:
        session.expires_at = expires_at
        session.save()
    return session


def get_user_from_session_token(token):
    """Получает пользователя по токену сессии"""
    try:
        session = Session.objects.select_related('user').get(
            session_token=token,
            expires_at__gt=datetime.utcnow()
        )
        if session.user.is_active:
            return session.user
    except Session.DoesNotExist:
        pass
    return None


def delete_session(token):
    """Удаляет сессию"""
    Session.objects.filter(session_token=token).delete()

