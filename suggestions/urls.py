from django.urls import path
from .views import manage_meditations,self_affirmation_complete, add_meditation, edit_meditation, delete_meditation, self_affirmation_step,game, breathing_exercises, breathing_circle, breathing_478, breathing_711, breathing_box, meditation, meditation_list, complete_meditation

urlpatterns = [
    path("self-affirmation/<int:step>/", self_affirmation_step, name="self_affirmation_step"),
    path('breathing-exercises/', breathing_exercises, name='breathing_exercises'),
    path('circlebreathing/',breathing_circle, name="breathing_circle"),
    path('4-7-8-breathing/', breathing_478, name="478breathing"),
    path('7-11-breathing/', breathing_711, name="711breathing"),
    path('box-breathing/', breathing_box, name="box_breathing"),
    path('game/<int:scene_id>/', game, name='game'),
    path('meditation/', meditation_list, name='meditation_list'),
    path('meditation/session/', meditation, name='meditation'),
    path('meditation/complete/<int:meditation_id>/', complete_meditation, name='complete_meditation'),
    path('meditations/manage/', manage_meditations, name='manage_meditations'),
    path('meditations/add/', add_meditation, name='add_meditation'),
    path('meditations/edit/<int:meditation_id>/', edit_meditation, name='edit_meditation'),
    path('meditations/delete/<int:meditation_id>/', delete_meditation, name='delete_meditation'),
    path('self-affirmation/complete/', self_affirmation_complete, name='self_affirmation_complete'),
]
