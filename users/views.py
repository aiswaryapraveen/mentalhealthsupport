from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import SignupForm, ProfessionalRegistrationForm,ProfessionalDetailsForm, ReviewForm,CustomUserForm, Professional1Form, ProfessionalDetailsForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from core.models import Goal, PersonalGoal, Notification, DailyGoal
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy, reverse
from django.contrib.messages.views import SuccessMessageMixin
from django.views.decorators.http import require_POST
from booking.models import Booking, Availability
import logging
from django.utils.html import format_html
from suggestions.models import SelfAffirmation, UserMeditation, YogaCompletion
from .models import CustomUser, Professional1, ProfessionalDetails, ProfessionalReview
from datetime import timedelta, date
from itertools import groupby
from django.db import transaction


@login_required
@require_POST
def reapply_professional(request):
    try:
        profile = request.user.professional1
        profile.is_approved = None  # back to pending
        profile.save()
        messages.success(request, "Your application is now resubmitted for approval.")
    except Professional1.DoesNotExist:
        messages.error(request, "No application found.")
    return redirect('mentor-reg')  # or wherever you need


def is_admin(user):
    return user.is_staff

@user_passes_test(is_admin)
def manage_reviews(request):
    reviews = ProfessionalReview.objects.select_related('user', 'professional').order_by('-created_at')
    return render(request, 'users/manage_reviews.html', {'reviews': reviews})

@user_passes_test(is_admin)
def admin_delete_review(request, review_id):
    review = get_object_or_404(ProfessionalReview, id=review_id)
    review.delete()

    user = review.user
    # Create notification for the user whose review was deleted
    notification_url = reverse('professional_profile', kwargs={'professional_id': review.professional.id})
    Notification.objects.create(
        user=user,
        message=format_html(
            '<a href="{}" style="color: #007bff; text-decoration: underline;">Your review for {} has been deleted by the admin.</a>',
            notification_url,
            review.professional.user.first_name  # Display the professional's first name in the notification
        ),
        notification_type="message"
    )
    messages.success(request, "Review deleted by admin.")
    return redirect('manage_reviews')  # Make sure this URL name exists

@user_passes_test(is_admin)
@csrf_exempt
def add_goal(request):
    if request.method == "POST":
        data = json.loads(request.body)
        goal_text = data.get("goal_text", "").strip()
        
        if goal_text:
            Goal.objects.create(text=goal_text)
            return JsonResponse({"success": "Goal added successfully!"})
        else:
            return JsonResponse({"error": "Goal text cannot be empty!"}, status=400)

@user_passes_test(is_admin)
@csrf_exempt
def delete_goal(request, goal_id):
    if request.method == "POST":
        try:
            goal = Goal.objects.get(id=goal_id)
            goal.delete()
            return JsonResponse({"success": "Goal deleted successfully!"})
        except Goal.DoesNotExist:
            return JsonResponse({"error": "Goal not found!"}, status=404)
@user_passes_test(is_admin)
def manage_goals(request):
    goals = Goal.objects.all()
    return render(request, "users/manage_goals.html", {"goals": goals})

@user_passes_test(is_admin)
def delete_goal(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id)
    goal.delete()
    messages.success(request, "Goal deleted successfully!")
    return redirect("manage_goals")

def add_personal_goal(request):
    if request.method == "POST":
        goal_text = request.POST.get("goal_text")
        if goal_text:
            PersonalGoal.objects.create(user=request.user, text=goal_text)
            return redirect("goals")
    return JsonResponse({"error": "Invalid request"}, status=400)

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignupForm()
    return render(request, 'users/signup.html', {'form': form})

MAX_PROFESSIONALS = 10  # You can move this to settings.py if needed
@login_required
def professional_registration(request):
    profile = None
    existing_application = Professional1.objects.filter(user=request.user).first()
    approved_count = Professional1.objects.filter(is_approved=True).count()

    if approved_count >= MAX_PROFESSIONALS and not existing_application:
        return render(request, 'users/mentor-reg.html', {
            'form': None,
            'existing_application': None,
            'max_reached': True
        })
    
 # Or show a page explaining why

    if request.method == 'POST':
        if existing_application:
            messages.error(request, "You already have a pending application.")
            return redirect('professional_registration')

        form = ProfessionalRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()

            admin_users = CustomUser.objects.filter(is_superuser=True)
            for admin in admin_users:
                notification_link = reverse("request_view")
                formatted_message = format_html(
                    'New professional request from <strong>{}</strong>. '
                    '<a href="{}" style="color: blue; text-decoration: underline;">Review Now</a>',
                    request.user.username,
                    notification_link
                )
                Notification.objects.create(
                    user=admin,
                    message=formatted_message,
                    notification_type="message"
                )

            messages.success(request, "Your request has been submitted for approval.")
            return redirect('mentor-reg')
    else:
        form = ProfessionalRegistrationForm()
    profile_details = None
    if request.user.is_authenticated:
        try:
            professional = Professional1.objects.get(user=request.user)
            try:
                profile_details = professional.details
            except ProfessionalDetails.DoesNotExist:
                profile_details = None
        except Professional1.DoesNotExist:
            profile_details = None
    return render(request, 'users/mentor-reg.html', {
        'form': form,
        'existing_application': existing_application,
        'max_reached': approved_count >= MAX_PROFESSIONALS,
        'profile_details': profile_details,
    })

@login_required
def user_management(request):
    if not request.user.is_superuser:
        messages.error(request, "Unauthorized access!")
        return redirect('dashboard')

    users = CustomUser.objects.filter(is_superuser=False, is_professional=False)  # Regular Users
    professionals = CustomUser.objects.filter(is_professional=True)  # Approved Professionals
    admins = CustomUser.objects.filter(is_superuser=True)  # Admins

    return render(request, 'users/user_management.html', {
        'users': users,
        'professionals': professionals,
        'admins': admins
    })

@login_required
def delete_user(request, user_id):
    if not request.user.is_superuser:
        return JsonResponse({'error': "Unauthorized action!"}, status=403)

    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    return JsonResponse({'success': "User deleted successfully!"})

logger = logging.getLogger(__name__)  # Debugging logger

@login_required
def remove_professional_status(request, user_id):
    if not request.user.is_superuser:
        return JsonResponse({'error': "Unauthorized action!"}, status=403)

    user = get_object_or_404(CustomUser, id=user_id)

    if user.is_professional:
        user.is_professional = False
        user.save(update_fields=['is_professional'])

        professional_request = Professional1.objects.filter(user=user).first()
        if professional_request:
            professional_request.is_approved = False
            professional_request.save(update_fields=['is_approved'])

            # ✅ Get all users who booked this professional
            booked_users = Booking.objects.filter(professional=professional_request).values_list('user', flat=True)

            logger.info(f"Found {len(booked_users)} users with bookings to notify.")
            
            # ✅ Notify users BEFORE deleting bookings
            notification_link = reverse("booking_page")
            for user_id in booked_users:
                try:
                    user_obj = CustomUser.objects.get(id=user_id)
                    formatted_message = format_html(
                        'Your booking with <strong>{}</strong> is no longer available. '
                        '<a href="{}" style="color: blue; text-decoration: underline;">Check Bookings</a>',
                        professional_request.user.username,
                        notification_link
                    )
                    Notification.objects.create(
                        user=user_obj,
                        message=formatted_message,
                        notification_type="warning"
                    )
                    logger.info(f"Notification sent to {user_obj.username} ({user_obj.id})")
                except CustomUser.DoesNotExist:
                    logger.error(f"User with ID {user_id} not found.")

            # ✅ Proceed with deletion
            deleted_availabilities, _ = Availability.objects.filter(professional=professional_request).delete()
            deleted_bookings, _ = Booking.objects.filter(professional=professional_request).delete()

            logger.info(f"Deleted {deleted_availabilities} availability slots.")
            logger.info(f"Deleted {deleted_bookings} bookings.")

            return JsonResponse({'success': f"{user.username} is no longer a professional, and their availability has been removed!"})

    return JsonResponse({'error': "This user is not a professional."}, status=400)


def forgotpassword(request):

    return render(request, 'users/forgotpassword.html')

class CustomPasswordResetView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    success_message = "An email with password reset instructions has been sent to your email."

@login_required
def profile_view(request):
    user = request.user

    # Goal completion and streak
    daily_goals = DailyGoal.objects.filter(user=user, completed=True)
    completed_goals_count = daily_goals.count()
    personal_goals = PersonalGoal.objects.filter(user=user, completed=True)
    total_goals_count = personal_goals.count()
    goaltotal = completed_goals_count + total_goals_count

    # Streak logic for goals
    goal_streak = 0
    last_completed_date = None
    for daily_goal in daily_goals.order_by('-date'):
        if last_completed_date is None or daily_goal.date == last_completed_date - timedelta(days=1):
            goal_streak += 1
            last_completed_date = daily_goal.date
        else:
            break

    # Fetch all affirmations
    affirmations = SelfAffirmation.objects.filter(user=user).order_by('-date')

    # Fetch completed meditations
    completed_meditations = UserMeditation.objects.filter(user=user).order_by('-completed_at')

    # Meditation streak logic
    meditation_dates_set = set(m.completed_at.date() for m in completed_meditations)
    today = date.today()
    past_30_days = [today - timedelta(days=i) for i in range(30)]

    meditation_streak = 0
    for d in past_30_days:
        if d in meditation_dates_set:
            meditation_streak += 1
        else:
            break

    # Group meditation sessions by date
    grouped_meditations = {}
    for d, items in groupby(completed_meditations, key=lambda x: x.completed_at.date()):
        grouped_meditations[d] = list(items)

    # Meditation calendar data
    meditation_calendar_data = {d: (d in meditation_dates_set) for d in reversed(past_30_days)}

    # For professionals only
    professional_data = None
    professional_details = None
    if user.is_professional:
        try:
            professional_data = Professional1.objects.select_related('user').get(user=user)
            professional_details = ProfessionalDetails.objects.filter(professional=professional_data).first()
        except Professional1.DoesNotExist:
            pass

    # Fetch reviews if professional
    reviews = None
    if user.is_professional and professional_data:
        reviews = ProfessionalReview.objects.filter(professional=professional_data).select_related('user').order_by('-created_at')

    # Fetch completed yoga sessions
    yoga_completions = YogaCompletion.objects.filter(user=user).select_related('session').order_by('-completed_at')

    # Group yoga sessions by completed date
    grouped_yoga_sessions = {}
    for d, items in groupby(yoga_completions, key=lambda x: x.completed_at.date()):
        grouped_yoga_sessions[d] = list(items)

    # Yoga streak and calendar data
    yoga_dates_set = set(y.completed_at.date() for y in yoga_completions)
    yoga_streak = 0
    for d in past_30_days:
        if d in yoga_dates_set:
            yoga_streak += 1
        else:
            break

    yoga_calendar_data = {d: (d in yoga_dates_set) for d in reversed(past_30_days)}
    day_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    return render(request, 'users/profile.html', {
        'user': user,
        'completed_goals_count': completed_goals_count,
        'goaltotal': goaltotal,
        'streak': goal_streak,
        'affirmations': affirmations,
        'completed_meditations': completed_meditations,
        'meditation_streak': meditation_streak,
        'grouped_meditations': grouped_meditations,
        'meditation_calendar_data': meditation_calendar_data,
        'professional_data': professional_data,
        'professional_details': professional_details,
        'reviews': reviews,
        'yoga_streak': yoga_streak,
        'yoga_calendar_data': yoga_calendar_data,
        'grouped_yoga_sessions': grouped_yoga_sessions,
        'day_labels': day_labels,
    })

@login_required
def switch_to_normal_user(request):
    if request.method == 'POST' and request.user.is_professional:
        try:
            with transaction.atomic():
                # Update user type
                request.user.is_professional = False
                request.user.save(update_fields=['is_professional'])

                # Delete professional profile (and its document)
                professional_profile = Professional1.objects.get(user=request.user)

                if professional_profile.qualification_document:
                    professional_profile.qualification_document.delete(save=False)

                professional_profile.delete()

                messages.success(request, "You have successfully switched to a normal user. Professional data has been removed.")
        except Professional1.DoesNotExist:
            messages.warning(request, "You did not have a professional profile to remove.")
    else:
        messages.error(request, "Invalid request.")

    return redirect('dashboard')  # or 'profile', as needed

@login_required
def update_professional_profile(request):
    if not request.user.is_professional:
        return redirect('dashboard')

    try:
        professional = Professional1.objects.get(user=request.user, is_approved=True)
    except Professional1.DoesNotExist:
        return redirect('dashboard')

    details, created = ProfessionalDetails.objects.get_or_create(professional=professional)

    if request.method == 'POST':
        form = ProfessionalDetailsForm(request.POST, request.FILES, instance=details)
        if form.is_valid():
            profile = form.save(commit=False)

            # Check if user selected "Remove Profile Picture"
            if 'remove_picture' in request.POST:
                if profile.profile_picture:
                    profile.profile_picture.delete(save=False)
                profile.profile_picture = None

            profile.save()
            return redirect('mentor-reg')
    else:
        form = ProfessionalDetailsForm(instance=details)

    return render(request, 'users/update_professional.html', {'form': form})

@login_required
def settings_view(request):
    user = request.user
    user_form = CustomUserForm(instance=user)
    professional_form = None
    details_form = None

    if user.is_professional:
        professional_obj = Professional1.objects.filter(user=user).first()
        details_obj = getattr(professional_obj, 'details', None)

        professional_form = Professional1Form(instance=professional_obj)
        details_form = ProfessionalDetailsForm(instance=details_obj)

    if request.method == 'POST':
        user_form = CustomUserForm(request.POST, instance=user)

        if user.is_professional:
            professional_form = Professional1Form(request.POST, request.FILES, instance=professional_obj)
            details_form = ProfessionalDetailsForm(request.POST, request.FILES, instance=details_obj)

            if user_form.is_valid() and professional_form.is_valid() and details_form.is_valid():
                user_form.save()
                professional_form.save()
                details_form.save()
                return redirect('settings')
        else:
            if user_form.is_valid():
                user_form.save()
                return redirect('settings')

    context = {
        'user_form': user_form,
        'professional_form': professional_form,
        'details_form': details_form,
        'is_professional': user.is_professional,
    }
    return render(request, 'users/settings.html', context)
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg, Count

@login_required
def leave_review(request, professional_id):
    professional = get_object_or_404(Professional1, id=professional_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.professional = professional
            review.save()

            # Create notification for the professional
            review_url = reverse('user_profile')

            # Notification for the professional about a new review
            Notification.objects.create(
                user=professional.user,
                message=format_html(
                    '<a href="{}" style="color: #007bff; text-decoration: underline;">You have received a new review from {}</a>',
                    review_url,
                    request.user.username
                ),
                notification_type="message"
            )
            return redirect('professional_profile', professional_id=professional.id)
        try:
            details = professional.details
            profile_picture = details.profile_picture if details.profile_picture else None
        except ObjectDoesNotExist:
            details = None
            profile_picture = None

        reviews = ProfessionalReview.objects.filter(professional=professional).order_by('-created_at')[:5]
        rating_avg = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        review_count = reviews.count()
        full_stars = int(rating_avg)
        half_star = 1 if (rating_avg - full_stars) >= 0.25 and (rating_avg - full_stars) < 0.75 else 0
        empty_stars = 5 - full_stars - half_star
        notifications = Notification.objects.filter(user=professional.user, is_read=False)

        context = {
            'professional': professional,
            'reviews': reviews,
            'details': details,
            'profile_picture': profile_picture,
            'review_form': form,  # <- this has the errors
            'availability_list': Availability.objects.filter(professional=professional),
            'review_count': review_count,
            'rating_avg': round(rating_avg, 1),
            'full_stars': full_stars,
            'half_star': half_star,
            'empty_stars': empty_stars,
            'notifications': notifications,
        }

        return render(request, 'booking/professional_profile.html', context)

    # GET request fallback (shouldn't happen normally)
    return redirect('professional_profile', professional_id=professional.id)
@login_required
def delete_review(request, review_id):
    review = get_object_or_404(ProfessionalReview, id=review_id, user=request.user)
    professional_id = review.professional.id
    review.delete()
    messages.success(request, "Your review was deleted successfully.")
    return redirect('professional_profile', professional_id)
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .forms import CustomChangePasswordForm

@login_required
def update_password(request):
    if request.method == 'POST':
        form = CustomChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Important!
            messages.success(request, 'Password changed successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomChangePasswordForm(user=request.user)

    return render(request, 'users/change_password_inline.html', {'form': form})
