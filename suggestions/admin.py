from django.contrib import admin
from .models import Meditation, UserMeditation, YogaSession

@admin.register(Meditation)
class MeditationAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')  # Show these fields in the list view
    search_fields = ('title',)  # Allow searching by title
    list_filter = ('title',)  # Add filters

@admin.register(UserMeditation)
class UserMeditationAdmin(admin.ModelAdmin):
    list_display = ('user', 'meditation', 'completed_at')  # Show these fields
    search_fields = ('user__username', 'meditation__title')  # Search by user or meditation title

@admin.register(YogaSession)
class YogaSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration', 'video_url')
    search_fields = ('title', 'description')