from django.contrib import admin
from users.models import User, Session


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'role']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['date_joined', 'updated_at']


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_token', 'expires_at', 'created_at', 'last_activity']
    list_filter = ['expires_at', 'created_at']
    search_fields = ['user__email', 'session_token']
    readonly_fields = ['created_at', 'last_activity']
