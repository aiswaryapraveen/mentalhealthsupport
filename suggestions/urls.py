from django.urls import path
from .views import self_affirmation_step,game, breathing_exercises, breathing_circle, breathing_478, breathing_711, breathing_box, meditation

urlpatterns = [
    path("self-affirmation/<int:step>/", self_affirmation_step, name="self_affirmation_step"),
    path('breathing-exercises/', breathing_exercises, name='breathing_exercises'),
    path('circlebreathing/',breathing_circle, name="breathing_circle"),
    path('4-7-8-breathing/', breathing_478, name="478breathing"),
    path('7-11-breathing/', breathing_711, name="711breathing"),
    path('box-breathing/', breathing_box, name="box_breathing"),
    path('game/<int:scene_id>/', game, name='game'),
    path('meditation/', meditation, name='meditation'),
]
