from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from permissions.models import BusinessElement, AccessRoleRule


def check_permission(element_name, action, check_owner=False, owner_getter=None):
    """
    Декоратор для проверки прав доступа к ресурсу.
    
    Args:
        element_name: имя бизнес-элемента (например, 'users', 'products')
        action: действие ('read', 'read_all', 'create', 'update', 'update_all', 'delete', 'delete_all')
        check_owner: нужно ли проверять, является ли пользователь владельцем объекта
        owner_getter: функция для получения владельца объекта (принимает request, возвращает owner_id)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # Проверка аутентификации
            if not request.user or not hasattr(request.user, 'id'):
                return Response(
                    {'error': 'Необходима аутентификация'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            user = request.user
            
            # Если пользователь - суперпользователь, пропускаем проверку
            if hasattr(user, 'is_superuser') and user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Проверяем роль пользователя
            if not user.role:
                return Response(
                    {'error': 'У пользователя нет роли'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Получаем бизнес-элемент
            try:
                element = BusinessElement.objects.get(name=element_name)
            except BusinessElement.DoesNotExist:
                return Response(
                    {'error': f'Бизнес-элемент "{element_name}" не найден'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Получаем правило доступа для роли и элемента
            try:
                rule = AccessRoleRule.objects.get(role=user.role, element=element)
            except AccessRoleRule.DoesNotExist:
                return Response(
                    {'error': 'Доступ запрещен'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Проверяем разрешение на действие
            permission_attr = f'{action}_permission'
            has_permission = getattr(rule, permission_attr, False)
            
            if not has_permission:
                # Если нет прямого разрешения, проверяем всеобщее разрешение для некоторых действий
                if action in ['read', 'update', 'delete']:
                    all_permission_attr = f'{action}_all_permission'
                    has_all_permission = getattr(rule, all_permission_attr, False)
                    if has_all_permission:
                        has_permission = True
                
                if not has_permission:
                    return Response(
                        {'error': 'Доступ запрещен'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            # Если нужно проверить владельца
            if check_owner and owner_getter:
                owner_id = owner_getter(request, *args, **kwargs)
                if owner_id and owner_id != user.id:
                    # Проверяем, есть ли разрешение на все объекты
                    all_permission_attr = f'{action}_all_permission'
                    has_all_permission = getattr(rule, all_permission_attr, False)
                    if not has_all_permission:
                        return Response(
                            {'error': 'Доступ запрещен. Вы не являетесь владельцем объекта'},
                            status=status.HTTP_403_FORBIDDEN
                        )
            
            return view_func(request, *args, **kwargs)
        
        return wrapped_view
    return decorator


def has_permission(user, element_name, action):
    """
    Проверяет, есть ли у пользователя право на действие с элементом.
    Используется в коде для дополнительных проверок.
    
    Args:
        user: объект пользователя
        element_name: имя бизнес-элемента
        action: действие
        
    Returns:
        bool: True если есть право, False если нет
    """
    if hasattr(user, 'is_superuser') and user.is_superuser:
        return True
    
    if not user.role:
        return False
    
    try:
        element = BusinessElement.objects.get(name=element_name)
        rule = AccessRoleRule.objects.get(role=user.role, element=element)
        permission_attr = f'{action}_permission'
        has_perm = getattr(rule, permission_attr, False)
        
        # Проверяем всеобщее разрешение для некоторых действий
        if not has_perm and action in ['read', 'update', 'delete']:
            all_permission_attr = f'{action}_all_permission'
            has_perm = getattr(rule, all_permission_attr, False)
        
        return has_perm
    except (BusinessElement.DoesNotExist, AccessRoleRule.DoesNotExist):
        return False

