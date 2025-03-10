from django.urls import path
from . import views  # Use 'views' instead of 'from .views import ...'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('about/', views.about_page, name='about'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('request/', views.request_view, name='request_view'),
    path('analyze-journal/', views.analyze_journal_entry, name='analyze_journal'),
]
