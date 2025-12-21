from django.urls import path
from permissions import views

urlpatterns = [
    path('roles/', views.list_roles, name='list_roles'),
    path('business-elements/', views.list_business_elements, name='list_business_elements'),
    path('access-rules/', views.list_access_rules, name='list_access_rules'),
    path('access-rules/create/', views.create_access_rule, name='create_access_rule'),
    path('access-rules/<int:rule_id>/', views.get_access_rule, name='get_access_rule'),
    path('access-rules/<int:rule_id>/update/', views.update_access_rule, name='update_access_rule'),
    path('access-rules/<int:rule_id>/delete/', views.delete_access_rule, name='delete_access_rule'),
]

