from django.urls import path
from django.contrib.auth import views as auth_views
from .views import signup_view, user_management, delete_user, remove_professional_status, professional_registration
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('mentorreg/',  professional_registration, name='mentor-reg'),
    path('manage-users/', user_management, name='user_management'),
    path('delete-user/<int:user_id>/', delete_user, name='delete_user'),
    path('remove-professional/<int:user_id>/', remove_professional_status, name='remove_professional'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

