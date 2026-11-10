from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Nurseon Profile', {'fields': ('role', 'specialization')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Nurseon Profile', {'fields': ('role', 'specialization')}),
    )