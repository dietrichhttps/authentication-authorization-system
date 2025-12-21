from django.contrib import admin
from permissions.models import Role, BusinessElement, AccessRoleRule


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']


@admin.register(BusinessElement)
class BusinessElementAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']


@admin.register(AccessRoleRule)
class AccessRoleRuleAdmin(admin.ModelAdmin):
    list_display = ['role', 'element', 'read_permission', 'read_all_permission', 
                    'create_permission', 'update_permission', 'update_all_permission',
                    'delete_permission', 'delete_all_permission']
    list_filter = ['role', 'element']
    search_fields = ['role__name', 'element__name']
