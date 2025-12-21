from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

from permissions.models import Role, BusinessElement, AccessRoleRule
from permissions.serializers import (
    RoleSerializer,
    BusinessElementSerializer,
    AccessRoleRuleSerializer,
    AccessRoleRuleCreateSerializer
)


def check_admin(user):
    """Проверяет, является ли пользователь администратором"""
    if not user or not hasattr(user, 'id'):
        return False
    if hasattr(user, 'is_superuser') and user.is_superuser:
        return True
    # Можно также проверить роль администратора
    if user.role and user.role.name.lower() == 'admin':
        return True
    return False


@api_view(['GET'])
def list_roles(request):
    """Список всех ролей (только для администратора)"""
    if not check_admin(request.user):
        return Response(
            {'error': 'Доступ запрещен. Требуются права администратора'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    roles = Role.objects.all()
    serializer = RoleSerializer(roles, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def list_business_elements(request):
    """Список всех бизнес-элементов (только для администратора)"""
    if not check_admin(request.user):
        return Response(
            {'error': 'Доступ запрещен. Требуются права администратора'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    elements = BusinessElement.objects.all()
    serializer = BusinessElementSerializer(elements, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def list_access_rules(request):
    """Список всех правил доступа (только для администратора)"""
    if not check_admin(request.user):
        return Response(
            {'error': 'Доступ запрещен. Требуются права администратора'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    rules = AccessRoleRule.objects.select_related('role', 'element').all()
    serializer = AccessRoleRuleSerializer(rules, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@csrf_exempt
def create_access_rule(request):
    """Создание нового правила доступа (только для администратора)"""
    if not check_admin(request.user):
        return Response(
            {'error': 'Доступ запрещен. Требуются права администратора'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = AccessRoleRuleCreateSerializer(data=request.data)
    if serializer.is_valid():
        rule = serializer.save()
        return Response(
            AccessRoleRuleSerializer(rule).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_access_rule(request, rule_id):
    """Получение правила доступа по ID (только для администратора)"""
    if not check_admin(request.user):
        return Response(
            {'error': 'Доступ запрещен. Требуются права администратора'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        rule = AccessRoleRule.objects.select_related('role', 'element').get(id=rule_id)
        serializer = AccessRoleRuleSerializer(rule)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except AccessRoleRule.DoesNotExist:
        return Response(
            {'error': 'Правило доступа не найдено'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT', 'PATCH'])
@csrf_exempt
def update_access_rule(request, rule_id):
    """Обновление правила доступа (только для администратора)"""
    if not check_admin(request.user):
        return Response(
            {'error': 'Доступ запрещен. Требуются права администратора'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        rule = AccessRoleRule.objects.get(id=rule_id)
        serializer = AccessRoleRuleCreateSerializer(rule, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                AccessRoleRuleSerializer(rule).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except AccessRoleRule.DoesNotExist:
        return Response(
            {'error': 'Правило доступа не найдено'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['DELETE'])
@csrf_exempt
def delete_access_rule(request, rule_id):
    """Удаление правила доступа (только для администратора)"""
    if not check_admin(request.user):
        return Response(
            {'error': 'Доступ запрещен. Требуются права администратора'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        rule = AccessRoleRule.objects.get(id=rule_id)
        rule.delete()
        return Response(
            {'message': 'Правило доступа успешно удалено'},
            status=status.HTTP_200_OK
        )
    except AccessRoleRule.DoesNotExist:
        return Response(
            {'error': 'Правило доступа не найдено'},
            status=status.HTTP_404_NOT_FOUND
        )
