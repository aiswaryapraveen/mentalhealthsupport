from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('', include('core.urls')),  # Landing, About, and Dashboard
    path('community/', include('community.urls')),
]
