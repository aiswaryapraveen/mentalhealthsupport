from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import SignupForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import ProfessionalRegistrationForm, GoalForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from core.models import Goal, PersonalGoal
from .models import CustomUser, Professional1
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin

def is_admin(user):
    return user.is_staff

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


@login_required
def professional_registration(request):
    profile = None
    existing_application = Professional1.objects.filter(user=request.user).first()  # Check if user already applied

    if request.method == 'POST':
        if existing_application:  # Prevent duplicate applications
            messages.error(request, "You already have a pending application.")
            return redirect('professional_registration')

        form = ProfessionalRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user  # Assign user
            profile.save()
            messages.success(request, "Your request has been submitted for approval.")
            return redirect('mentor-reg')

    else:
        form = ProfessionalRegistrationForm()

    return render(request, 'users/mentor-reg.html', {
        'form': form,
        'existing_application': existing_application
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

@login_required
def remove_professional_status(request, user_id):
    if not request.user.is_superuser:
        return JsonResponse({'error': "Unauthorized action!"}, status=403)

    user = get_object_or_404(CustomUser, id=user_id)

    if user.is_professional:  # Directly check the field instead of hasattr()
        user.is_professional = False
        user.save(update_fields=['is_professional'])

        professional_request = Professional1.objects.filter(user=user).first()
        if professional_request:
            professional_request.is_approved = False
            professional_request.save(update_fields=['is_approved'])
        return JsonResponse({'success': f"{user.username} is no longer a professional!"})

    return JsonResponse({'error': "This user is not a professional."}, status=400)


def forgotpassword(request):

    return render(request, 'users/forgotpassword.html')

class CustomPasswordResetView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    success_message = "An email with password reset instructions has been sent to your email."