from django.urls import path
from .views import bubble_pop_game,relaxation_games_home,save_bubble_score,manage_meditations,self_affirmation_complete, add_meditation, edit_meditation, delete_meditation, self_affirmation_step,game, breathing_exercises, breathing_circle, breathing_478, breathing_711, breathing_box, meditation, meditation_list, complete_meditation
from . import views
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
    path('relaxation-games/', relaxation_games_home, name='relaxation_games_home'),
    path('bubble-pop/', bubble_pop_game, name='bubble_pop_game'),
    path('save-bubble-score/', save_bubble_score, name='save_bubble_score'),
    path('memory-game/', views.memory_game_view, name='memory_game'),
    path('save-memory-score/', views.save_memory_score, name='save_memory_score'),
    path('focus-maze/', views.focus_maze, name='focus_maze'),
    path('save-focus-maze-score/', views.save_focus_maze_score, name='save_focus_maze_score'),
    path('four-in-a-row/', views.four_in_a_row_view, name='four_in_a_row'),
]
