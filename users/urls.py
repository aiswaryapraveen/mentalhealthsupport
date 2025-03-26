from django.urls import path
from django.contrib.auth import views as auth_views
from .views import signup_view, user_management, add_personal_goal, delete_user, remove_professional_status, professional_registration, add_goal, delete_goal,manage_goals, forgotpassword
from django.conf import settings
from django.conf.urls.static import static
from .views import CustomPasswordResetView

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('mentorreg/',  professional_registration, name='mentor-reg'),
    path('manage-users/', user_management, name='user_management'),
    path('delete-user/<int:user_id>/', delete_user, name='delete_user'),
    path('remove-professional/<int:user_id>/', remove_professional_status, name='remove_professional'),
    path("manage-goals/", manage_goals, name="manage_goals"),
    path("add-goal/", add_goal, name="add-goal"),
    path("delete-goal/<int:goal_id>/", delete_goal, name="delete_goal"),
    path('add-personal-goal/', add_personal_goal, name='add_personal_goal'),
    path('forgotpass/', forgotpassword, name='forgotpass'),
    path('reset_password/', CustomPasswordResetView.as_view(), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="users/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"), name='password_reset_complete'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

