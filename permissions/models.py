from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Role(models.Model):
    """Роли пользователей в системе"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'roles'
    
    def __str__(self):
        return self.name


class BusinessElement(models.Model):
    """Объекты бизнес-приложения, к которым осуществляется доступ"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'business_elements'
    
    def __str__(self):
        return self.name


class AccessRoleRule(models.Model):
    """Правила доступа роли к элементам бизнес-приложения"""
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='access_rules'
    )
    element = models.ForeignKey(
        BusinessElement,
        on_delete=models.CASCADE,
        related_name='access_rules'
    )
    
    # Права на чтение
    read_permission = models.BooleanField(default=False)  # Чтение своих объектов
    read_all_permission = models.BooleanField(default=False)  # Чтение всех объектов
    
    # Права на создание
    create_permission = models.BooleanField(default=False)
    
    # Права на обновление
    update_permission = models.BooleanField(default=False)  # Обновление своих объектов
    update_all_permission = models.BooleanField(default=False)  # Обновление всех объектов
    
    # Права на удаление
    delete_permission = models.BooleanField(default=False)  # Удаление своих объектов
    delete_all_permission = models.BooleanField(default=False)  # Удаление всех объектов
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'access_roles_rules'
        unique_together = ['role', 'element']
        indexes = [
            models.Index(fields=['role', 'element']),
        ]
    
    def __str__(self):
        return f"{self.role.name} -> {self.element.name}"
