from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'age', 'gender', 'is_professional', 'is_staff', 'is_active')
    list_filter = ('gender', 'is_professional', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'age', 'dob', 'gender')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Professional Status', {'fields': ('is_professional',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'age', 'dob', 'gender', 'is_professional'),
        }),
    )
from core.models import Goal

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("text",)