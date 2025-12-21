from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta

from users.models import User
from users.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserUpdateSerializer
)
from users.utils import generate_jwt_token, create_session, delete_session


@api_view(['POST'])
@csrf_exempt
def register(request):
    """Регистрация нового пользователя"""
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = User.objects.create_user(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            first_name=serializer.validated_data.get('first_name', ''),
            last_name=serializer.validated_data.get('last_name', ''),
            middle_name=serializer.validated_data.get('middle_name', ''),
        )
        
        # Генерируем токен
        token = generate_jwt_token(user.id)
        create_session(user, token)
        
        response = Response({
            'message': 'Пользователь успешно зарегистрирован',
            'user': UserProfileSerializer(user).data,
            'token': token
        }, status=status.HTTP_201_CREATED)
        
        # Устанавливаем cookie с session_id
        expires = datetime.utcnow() + timedelta(days=7)
        response.set_cookie(
            'session_id',
            token,
            expires=expires,
            httponly=True,
            samesite='Lax'
        )
        
        return response
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@csrf_exempt
def login(request):
    """Вход пользователя в систему"""
    serializer = UserLoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {'error': 'Неверный email или пароль'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.check_password(password):
        return Response(
            {'error': 'Неверный email или пароль'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        return Response(
            {'error': 'Аккаунт деактивирован'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Генерируем токен
    token = generate_jwt_token(user.id)
    create_session(user, token)
    
    response = Response({
        'message': 'Успешный вход',
        'user': UserProfileSerializer(user).data,
        'token': token
    }, status=status.HTTP_200_OK)
    
    # Устанавливаем cookie с session_id
    expires = datetime.utcnow() + timedelta(days=7)
    response.set_cookie(
        'session_id',
        token,
        expires=expires,
        httponly=True,
        samesite='Lax'
    )
    
    return response


@api_view(['POST'])
@csrf_exempt
def logout(request):
    """Выход пользователя из системы"""
    # Удаляем сессию по токену из header
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split('Bearer ')[1].strip()
        delete_session(token)
    
    # Удаляем сессию по cookie
    session_token = request.COOKIES.get('session_id')
    if session_token:
        delete_session(session_token)
    
    response = Response({'message': 'Успешный выход'}, status=status.HTTP_200_OK)
    response.delete_cookie('session_id')
    
    return response


@api_view(['GET'])
def profile(request):
    """Получение профиля текущего пользователя"""
    if not request.user or not hasattr(request.user, 'id'):
        return Response(
            {'error': 'Необходима аутентификация'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@csrf_exempt
def update_profile(request):
    """Обновление профиля пользователя"""
    if not request.user or not hasattr(request.user, 'id'):
        return Response(
            {'error': 'Необходима аутентификация'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Профиль успешно обновлен',
            'user': UserProfileSerializer(request.user).data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@csrf_exempt
def delete_account(request):
    """Мягкое удаление аккаунта пользователя"""
    if not request.user or not hasattr(request.user, 'id'):
        return Response(
            {'error': 'Необходима аутентификация'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    user = request.user
    user.soft_delete()
    
    # Удаляем все сессии пользователя
    from users.models import Session
    Session.objects.filter(user=user).delete()
    
    response = Response({'message': 'Аккаунт успешно удален'}, status=status.HTTP_200_OK)
    response.delete_cookie('session_id')
    
    return response
