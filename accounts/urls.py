from django.urls import path, include
from .views import (
    AdminStudentDeleteView,
    AdminStudentUpdateView,
    AdminToggleUserRoleView,
    AdminUserDeleteView,
    AdminUserPasswordView,
    AdminUserUpdateView,
    ProfileUpdateView,
    RoleDashboardRedirectView,
    SignUpView,
)

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
    path('dashboard-redirect/', RoleDashboardRedirectView.as_view(), name='role_dashboard'),

    # Admin User management
    path('users/<int:user_id>/edit/', AdminUserUpdateView.as_view(), name='admin_user_edit'),
    path('users/<int:user_id>/password/', AdminUserPasswordView.as_view(), name='admin_user_password'),
    path('users/<int:user_id>/toggle-role/', AdminToggleUserRoleView.as_view(), name='admin_user_toggle_role'),
    path('users/<int:user_id>/delete/', AdminUserDeleteView.as_view(), name='admin_user_delete'),

    # Backward-compatible routes (Changed student_id to user_id)
    path('students/<int:user_id>/edit/', AdminStudentUpdateView.as_view(), name='admin_student_edit'),
    path('students/<int:user_id>/delete/', AdminStudentDeleteView.as_view(), name='admin_student_delete'),

    path('', include('django.contrib.auth.urls')),
]