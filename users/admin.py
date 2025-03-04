from django.contrib import admin

# Register your models here.
# from .models import ProfessionalProfile

# @admin.register(ProfessionalProfile)
# class ProfessionalProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'specialization', 'experience', 'is_approved')
#     list_filter = ('is_approved', 'specialization')
#     search_fields = ('user__username', 'qualification_details', 'specialization')
#     readonly_fields = ('qualification_document',)  # Display uploaded file without allowing modification
#     fieldsets = (
#         ('User Information', {
#             'fields': ('user', 'is_approved'),
#         }),
#         ('Professional Details', {
#             'fields': ('specialization', 'experience', 'qualification_details', 'qualification_document'),
#         }),
#     )

#     def has_add_permission(self, request):
#         """Restrict adding new ProfessionalProfile instances from the admin panel."""
#         return False  # Prevent manual creation in the admin panel

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
