from django.urls import path
from . import views

urlpatterns = [
    path('', views.community_feed, name='community_feed'),
    path('create/', views.create_post, name='create_post'),
    path('<int:post_id>/reply/', views.reply_to_post, name='reply_post'),  # ✅ Add this
    path('<int:reply_id>/reply-to-replay/', views.reply_to_reply, name='reply_reply'),  # ✅ Add this
    path('<int:post_id>/delete/', views.delete_post, name='delete_post'),  # ✅ For deleting posts
    path('<int:reply_id>/delete-reply/', views.delete_reply, name='delete_reply'),

]
