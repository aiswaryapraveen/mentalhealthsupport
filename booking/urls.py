from django.urls import path
from .views import manage_availability,delete_booking, booking_page, professional_profile, delete_availability, booking, booking_view, update_booking_status

urlpatterns = [
    path('', booking_page, name='booking_page'),
    path('profile/<int:professional_id>/', professional_profile, name='professional_profile'),
    path('manage-availability/', manage_availability, name='manage_availability'),
    path('booking/<int:professional_id>/', booking, name='booking'),  # Lowercase 'booking'
    path('booking-view/', booking_view, name='booking_view'),
    path('booking/update/<int:booking_id>/<str:status>/', update_booking_status, name='update_booking_status'),
    path('booking/delete/<int:booking_id>/', delete_booking, name='delete_booking'),
    path('delete-availability/<int:availability_id>/', delete_availability, name='delete_availability'),    
]
