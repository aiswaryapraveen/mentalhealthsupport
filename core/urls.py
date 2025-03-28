from django.urls import path
from . import views  # Use 'views' instead of 'from .views import ...'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('about/', views.about_page, name='about'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('request/', views.request_view, name='request_view'),
    path('analyze-journal/', views.analyze_journal_entry, name='analyze_journal'),
    path("complete-goal/<int:goal_id>/", views.complete_goal, name="complete_goal"),
    path('complete-personal-goal/<int:goal_id>/', views.complete_personal_goal, name='complete_personal_goal'),
    path('goals/', views.goals_view, name='goals'),
    path("delete-personal-goal/<int:goal_id>/", views.delete_personal_goal, name="delete_personal_goal"),
    path("notifications/", views.notifications_view, name="notifications"),
    path("notifications/read/<int:notification_id>/", views.mark_notification_as_read, name="mark_notification_as_read"),
    path('notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path("notifications/mark-all-read/", views.mark_all_notifications_as_read, name="mark_all_notifications_as_read"),
    path('heal/', views.heal, name='heal'),
]
