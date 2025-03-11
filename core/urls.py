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

]
