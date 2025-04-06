from django.urls import path
from django.contrib.auth import views as auth_views
from .views import signup_view,leave_review,manage_reviews, delete_review, admin_delete_review, settings_view, update_professional_profile, profile_view,reapply_professional,switch_to_normal_user, user_management, add_personal_goal, delete_user, remove_professional_status, professional_registration, add_goal, delete_goal,manage_goals, forgotpassword
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
    path('profile/', profile_view, name='user_profile'),
    path('switch-to-normal/', switch_to_normal_user, name='switch_to_normal_user'),
    path('reapply/', reapply_professional, name='reapply_professional'),
    path('update-professional-profile/', update_professional_profile, name='update_professional_profile'),
    path('settings/', settings_view, name='settings'),
    path('professionals/<int:professional_id>/review/', leave_review, name='leave_review'),
    path('review/delete/<int:review_id>/', delete_review, name='delete_review'),
    path('admin/manage-reviews/', manage_reviews, name='manage_reviews'),
    path('admin/review/delete/<int:review_id>/', admin_delete_review, name='admin_delete_review'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

