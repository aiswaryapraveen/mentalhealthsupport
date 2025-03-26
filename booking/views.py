from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Availability, Booking
from .forms import AvailabilityForm
from .forms import BookingForm
from django.contrib import messages
from core.models import Notification
from django.utils.html import format_html
from django.urls import reverse

@login_required
def manage_availability(request):
    # Check if the user is a professional
    if not request.user.is_professional:
        return render(request, 'booking/manage_availability.html', {
            'message': "You are not a professional, so you cannot add availability.",
            'is_professional': False
        })

    # Try to get the professional profile
    professional = getattr(request.user, 'professional1', None)
    if not professional:
        return render(request, 'booking/manage_availability.html', {
            'message': "You are a professional but your profile is not set up yet.",
            'is_professional': False
        })

    # Get availability slots for the professional
    availabilities = Availability.objects.filter(professional=professional)  

    if request.method == "POST":
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            availability = form.save(commit=False)
            availability.professional = professional
            availability.save()
            return redirect('manage_availability')

    form = AvailabilityForm()
    return render(request, 'booking/manage_availability.html', {
        'form': form,
        'availabilities': availabilities,
        'is_professional': True
    })

@login_required
def delete_availability(request, availability_id):
    availability = get_object_or_404(Availability, id=availability_id)

    # Ensure only the professional who created the availability can delete it
    if request.user != availability.professional.user:
        return redirect('manage_availability')  # Redirect if unauthorized

    availability.delete()
    return redirect('manage_availability')  # Redirect after deletion

from django.shortcuts import render, get_object_or_404
from .models import Professional1

from django.shortcuts import render
from users.models import Professional1
from django.utils.timezone import now
from booking.models import Availability
def booking_page(request):
    specialization_filter = request.GET.get("specialization", "").strip()
    # Get all approved professionals
    professionals = Professional1.objects.filter(is_approved=True)

    if specialization_filter:
        professionals = professionals.filter(specialization__icontains=specialization_filter)

    today = now().date()
    # Get all available slots (not booked)
    availability_list = Availability.objects.filter(date__gte=today).order_by('date', 'start_time')

    user_bookings = Booking.objects.filter(user=request.user, status="Confirmed", availability__date__gte=today)
    context = {
        "professionals": professionals,
        "availability_list": availability_list,
        "specialization_filter": specialization_filter,
        'bookings': user_bookings
    }

    return render(request, "booking/booking_page.html", context)

def professional_profile(request, professional_id):
    professional = get_object_or_404(Professional1, id=professional_id)
    availability_list = Availability.objects.filter(professional=professional).order_by('date', 'start_time')

    return render(request, 'booking/professional_profile.html', {
        'professional': professional,
        'availability_list': availability_list
    })

@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Ensure only the assigned professional can delete the booking
    if request.user != booking.professional.user:
        messages.error(request, "You are not authorized to delete this booking.")
        return redirect('booking_view')

    # Free up the slot if booking was confirmed
    if booking.status == "Confirmed":
        availability = booking.availability
        availability.booked_count = max(0, availability.booked_count - 1)  # Prevent negative values
        availability.save()
    
    # ✅ Notify Professional about Canceled Booking
    Notification.objects.create(
        user=booking.professional.user,
        message=f"Your appointment with {booking.user.first_name} has been canceled.",
        notification_type="appointment"
    )
    booking.delete()
    messages.success(request, "Booking has been successfully deleted/rejected.")
    return redirect('booking_view')

from django.utils.timezone import localdate
from django.urls import reverse

@login_required
def booking(request, professional_id):
    professional = get_object_or_404(Professional1, id=professional_id)
    form = BookingForm(professional=professional)
    available_slots = Availability.objects.filter(professional=professional).order_by('date', 'start_time')

    if request.method == "POST":
        form = BookingForm(request.POST, professional=professional)
        if form.is_valid():
            availability = form.cleaned_data['availability_id']
            booking_date = availability.date

            # Prevent user from booking the same professional more than once per day
            existing_booking = Booking.objects.filter(
                user=request.user,
                professional=professional,
                availability__date=booking_date
            ).exists()

            if existing_booking:
                messages.error(request, "You can only book one session per day with this professional.")
                return redirect(reverse("booking", args=[professional_id]))  # Redirect instead of rendering
            else:
                # Create a Pending booking (approved only by the professional)
                Booking.objects.create(
                    user=request.user,
                    professional=professional,
                    availability=availability,
                    status="Pending"
                )
                Notification.objects.create(
                user=professional.user,
                message=format_html(
                    '<a href="{}" style="color: #007bff; text-decoration: underline;">New booking request from {}.</a>',
                    reverse("booking_view"),  # Redirect to booking management page
                    request.user.first_name
                ),
                notification_type="appointment"
            )
                messages.success(request, "Booking request submitted! Waiting for approval.")
                return redirect(reverse("booking", args=[professional_id]))  # Redirect after success

    for slot in available_slots:
        slot.remaining_spots = max(0, slot.max_capacity - slot.booked_count)  # Ensure no negative values

    return render(request, "booking/booking.html", {
        "professional": professional,
        "form": form,
        "available_slots": available_slots
    })

@login_required
def booking_view(request):

    if not hasattr(request.user, 'professional1'):
        messages.error(request, "Access denied: Only professionals can view bookings.")
        return redirect('booking_view')
    # Fetch professional's bookings
    professional = request.user.professional1
    bookings = Booking.objects.filter(professional=professional).order_by('-booked_at')

    return render(request, 'booking/booking_management.html', {
        'bookings': bookings
    })


@login_required
def update_booking_status(request, booking_id, status):
    booking = get_object_or_404(Booking, id=booking_id)
    professional_name = booking.professional.user.first_name
    # Ensure only the correct professional can update the booking
    if request.user != booking.professional.user:
        messages.error(request, "You are not authorized to update this booking.")
        return redirect('booking_view')

    booking.status = status
    booking.save()

    if status == "Confirmed":
        availability = booking.availability

        # Decrease available spots only when confirmed
        if availability.booked_count < availability.max_capacity:
            availability.booked_count += 1
            availability.save()

        # ✅ Create Notification for the User (Booking Confirmed)
        # Generate dynamic URL for the user's booking details
        
        booking_url = reverse("booking_page") # Update "booking_detail" to match your URL name

        Notification.objects.create(
            user=booking.user,
            message=format_html(
                '<a href="{}" style="color: #007bff; text-decoration: underline;">Your appointment with {} has been confirmed!</a>',
                booking_url,
                professional_name,  # Dynamic URL
            ),
            notification_type="appointment"
        )
         # ✅ Notify Professional about Confirmation
        Notification.objects.create(
            user=booking.professional.user,
            message=f"You have confirmed an appointment with {booking.user.first_name}.",
            notification_type="appointment"
        )
    elif status == "Rejected":
        # ✅ Create Notification for the User (Booking Rejected)
        Notification.objects.create(
            user=booking.user,
            message=f"Your appointment with {professional_name} has been rejected.",
            notification_type="appointment"
        )
        # ✅ Notify Professional about Rejection
        Notification.objects.create(
            user=booking.professional.user,
            message=f"You have rejected an appointment with {booking.user.first_name}.",
            notification_type="appointment"
        )

    messages.success(request, f"Booking status updated to {status}.")
    return redirect('booking_view')

