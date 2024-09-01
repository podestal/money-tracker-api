"""
Core admin customization.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    add_fieldsets = (
            (None, {
                'classes': ('wide'),
                'fields': ('username', 
                           'password1', 
                           'password2', 
                           'email', 
                           'first_name', 
                           'last_name'),
            }
        ),
    )
