from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import JournalEntry, DailyGoal, Goal, PersonalGoal
from users.models import Professional1, CustomUser
import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from collections import defaultdict
from datetime import timedelta, date
from textblob import TextBlob
import re
import string
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from django.http import JsonResponse
from core.models import Notification

# In core/views.py
from django.shortcuts import render

def heal(request):
    return render(request, 'core/heal.html')


def landing_page(request):
    return render(request, 'core/landing.html')

def about_page(request):
    return render(request, 'core/about.html')

def goals_view(request):
    return render(request, 'core/goals.html')
from core.models import Notification
from django.urls import reverse
from django.utils.html import format_html
from booking.models import Booking, Availability
@login_required
def request_view(request):
    if not request.user.is_superuser:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('dashboard')
    else:     
        profiles = Professional1.objects.all()

        if request.method == 'POST':
            profile_id = request.POST.get('profile_id')
            profile = get_object_or_404(Professional1, id=profile_id)

            if 'delete' in request.POST:
                # Delete the associated qualification document only when deleting the profile
                if profile.qualification_document:
                    file_path = os.path.join(settings.MEDIA_ROOT, str(profile.qualification_document))
                    if os.path.exists(file_path):
                        os.remove(file_path)

                profile.delete()
                messages.success(request, f"Professional profile for {profile.user.username} has been deleted along with their document.")
                return redirect('request_view')

            if 'approve' in request.POST:
                profile.is_approved = True
                profile.user.is_professional = True
                profile.user.save()
                profile.save()
                messages.success(request, f"Professional profile for {profile.user.username} has been approved.")
                return redirect('request_view')

            if 'reject' in request.POST:
                profile.is_approved = False
                profile.user.is_professional = False
                profile.user.save()
                profile.save()

                # ✅ Get all users who booked this professional
                booked_users = Booking.objects.filter(professional=profile).values_list('user', flat=True)

                # ✅ Notify users BEFORE deleting bookings
                notification_link = reverse("booking_page")
                for user_id in booked_users:
                    try:
                        user_obj = CustomUser.objects.get(id=user_id)
                        formatted_message = format_html(
                            'Your booking with <strong>{}</strong> is no longer available. '
                            '<a href="{}" style="color: blue; text-decoration: underline;">Check Bookings</a>',
                            profile.user.username,
                            notification_link
                        )
                        Notification.objects.create(
                            user=user_obj,
                            message=formatted_message,
                            notification_type="message"
                        )
                    except CustomUser.DoesNotExist:
                        pass  # Skip if user does not exist

                # ✅ Remove all availability slots
                Availability.objects.filter(professional=profile).delete()
                
                # ✅ Remove all bookings for this professional
                Booking.objects.filter(professional=profile).delete()

                messages.success(request, f"Professional profile for {profile.user.username} has been rejected, and their availability has been removed.")
                return redirect('request_view')

        return render(request, 'core/request.html', {'profiles': profiles})
from datetime import date
from django.utils import timezone
@login_required
def goals_view(request):

    user_goals =[]
    user_goals1=[]
    combined_streak = 0
    completed_personal_goals_percentage = 0
    completed_daily_goals_percentage = 0

    if not request.user.is_superuser and not request.user.is_professional:
        assign_daily_goals(request.user)
        today = timezone.now().date()
        user_goals = DailyGoal.objects.filter(user=request.user, date=date.today())
        user_goals1 = PersonalGoal.objects.filter(user=request.user, date=today)
        user_goals_previous = PersonalGoal.objects.filter(user=request.user).exclude(date=date.today())  
        total_personal_goals = user_goals1.count()
        completed_personal_goals = user_goals1.filter(completed = True).count()

        # Calculate completed personal goals percentage (only count goals completed today)
        total_personal_goals_today = user_goals1.filter(date=today).count()  # Assuming 'created_at' is the field tracking goal creation
        completed_personal_goals_today = user_goals1.filter(completed=True, date=today).count()

        if total_personal_goals_today > 0:
            completed_personal_goals_percentage = (completed_personal_goals_today / total_personal_goals_today) * 100
        else:
            completed_personal_goals_percentage = 0

        # completed_personal_goals_percentage = (completed_personal_goals / total_personal_goals) * 100 if total_personal_goals > 0 else 0

        total_daily_goals = user_goals.count()
        completed_daily_goals = user_goals.filter(completed=True).count()

        completed_daily_goals_percentage = (completed_daily_goals / total_daily_goals) * 100 if total_daily_goals > 0 else 0

        combined_streak = calculate_combined_streak(request.user)

    return render(request, "core/goals.html", {
        "user_goals": user_goals,
        "user_goals1": user_goals1,
        "user_goals_previous": user_goals_previous,
        "completed_personal_goals_percentage": completed_personal_goals_percentage,
        "completed_daily_goals_percentage": completed_daily_goals_percentage,
        "combined_streak": combined_streak,
    })

@login_required
def dashboard(request):
    total_users = CustomUser.objects.count() if request.user.is_superuser else None
    total_professionals = CustomUser.objects.filter(is_professional=True).count() if request.user.is_superuser else None
    pending_approvals = Professional1.objects.filter(is_approved=False).count() if request.user.is_superuser else 0

    grouped_entries = {}
    if not request.user.is_superuser and not request.user.is_professional:
        if request.method == "POST":
            journal_text = request.POST.get("journal_entry")
            if journal_text.strip():
                JournalEntry.objects.create(user=request.user, text=journal_text)
            return redirect("dashboard")

        raw_entries = JournalEntry.objects.filter(user=request.user).order_by("-created_at")
        grouped_entries = defaultdict(list)
        for entry in raw_entries:
            grouped_entries[entry.created_at.date()].append(entry)

    return render(request, "core/dashboard.html", {
        "entries": dict(grouped_entries) if not request.user.is_superuser else None,
        "total_users": total_users or 0,
        "total_professionals": total_professionals or 0,
        "pending_approvals": pending_approvals or 0,
    })

def calculate_combined_streak(user):
    streak = 0
    today = date.today()
    
    print("Today's date:", today)

    week_start = today - timedelta(days=7)

    # Fetch completed daily and personal goals for the last 7 days
    completed_goals = DailyGoal.objects.filter(
        user=user,
        date__gte=week_start,
        completed=True
    ).values_list('date', flat=True)

    completed_personal_goals = PersonalGoal.objects.filter(
        user=user,
        date__gte=week_start,
        completed=True
    ).values_list('date', flat=True)

    print("Completed Daily Goals:", list(completed_goals))
    print("Completed Personal Goals:", list(completed_personal_goals))
    
    # Combine all completed goal dates
    completed_goal_dates = set(completed_goals) | set(completed_personal_goals)

    print("Combined Completed Goal Dates:", completed_goal_dates)
    # Loop through the last 7 days to calculate streak
    # 
    
    current_day = today

    while current_day in completed_goal_dates:
        streak += 1
        current_day -= timedelta(days=1)

    print(f"Current streak: {streak}")
    return int(streak)


# Load ML model and preprocessing tools
MODEL_PATH = os.path.join(settings.BASE_DIR, "core/ml_models/mental_health_model_ref.h5")
TOKENIZER_PATH = os.path.join(settings.BASE_DIR, "core/ml_models/tokenizer_ref.pkl")
ENCODER_PATH = os.path.join(settings.BASE_DIR, "core/ml_models/label_encoder_ref.pkl")

model = tf.keras.models.load_model(MODEL_PATH)

with open(TOKENIZER_PATH, "rb") as f:
    tokenizer = pickle.load(f)

with open(ENCODER_PATH, "rb") as f:
    encoder = pickle.load(f)

# Function to clean input text
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\d+', '', text)  # Remove numbers
    text = text.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
    return text

# Function to predict mental health status
def predict_mental_health(text):
    cleaned_text = clean_text(text)
    seq = tokenizer.texts_to_sequences([cleaned_text])
    padded = pad_sequences(seq, maxlen=100)
    prediction = model.predict(padded)
    label = encoder.inverse_transform([np.argmax(prediction)])
    return label[0]
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    lowered = text.lower()

    # Masked emotional cues (neutral-sounding but emotionally loaded)
    masked_emotion_phrases = {
        "everything is fine": "overwhelmed",
        "just fine": "overwhelmed",
        "smiling on the outside": "depressed",
        "i’m okay": "overwhelmed",
        "been better but also worse": "calm",
    }
    for phrase, label in masked_emotion_phrases.items():
        if phrase in lowered:
            return label

    # Critical keywords
    suicidal_keywords = ['disappear', 'worthless', 'can’t take it', 'no reason to go on', 'want to die', 'give up', 'end it all','better off without me']
    depressed_keywords = ['empty', 'no energy', 'don’t care', 'lost interest', 'tired of everything', 'breaking inside']
    anxiety_keywords = ['panic', 'nervous', 'heart racing', 'uneasy', 'what if', 'can’t breathe']
    stress_keywords = ['pressured', 'deadline', 'too much', 'stressed', 'burnt out']

    # Keyword-based overrides
    if any(word in lowered for word in suicidal_keywords):
        return 'suicidal'
    elif any(word in lowered for word in depressed_keywords):
        return 'depressed'
    elif any(word in lowered for word in anxiety_keywords):
        return 'anxiety'
    elif any(word in lowered for word in stress_keywords):
        return 'stress'

    # VADER sentiment analysis fallback
    scores = analyzer.polarity_scores(text)
    compound = scores['compound']

    if compound >= 0.7:
        return 'happy'
    elif compound >= 0.4:
        return 'hopeful'
    elif compound >= 0.1:
        return 'calm'
    elif compound > -0.4:
        return 'overwhelmed'
    else:
        return 'depressed'

# Sample suggestions with labels and URLs
# SUGGESTIONS_POOL = {
#     'Breathing Exercise': '/suggestions/breathing-exercises/',
#     'Try Meditation': '/suggestions/meditation/',
#     'Workout': '/dashboard/',
#     'Write Self-Affirmations': '/suggestions/self-affirmation/1/',
#     'Do Yoga': '/dashboard/',
#     'Distraction Game': '/suggestions/game/1/',
#     'Talk to Someone': '/community/',
#     'Book a Session': '/booking/',
# }
SUGGESTIONS_BY_STATUS = {
    "suicidal": {
        "suggestions": [
            ("Talk to Someone", "/community/"),
            ("Book a Session", "/booking/"),
            ("Write Self-Affirmations", "/suggestions/self-affirmation/1/"),
            ("Try Guided Meditation", "/suggestions/meditation/")
        ],
        "helplines": [
            {
                "name": "iCall",
                "number": "9152987821",
                "description": "Confidential emotional support.",
                "availability": "Mon–Sat, 10am–8pm"
            },
            {
                "name": "AASRA",
                "number": "91-9820466726",
                "description": "24/7 suicide prevention helpline.",
                "availability": "24/7"
            },
            {
                "name": "Samaritans Mumbai",
                "number": "91-8422984528",
                "description": "Safe space for emotional distress or suicidal thoughts.",
                "availability": "5pm to 9pm, all days"
            }
        ]
    },

    "depressed": {
        "suggestions": [
            ("Listen to Uplifting Meditation", "/suggestions/meditation/"),
            ("Write Self-Affirmations", "/suggestions/self-affirmation/1/"),
            ("Play a Light Game", "/suggestions/game/1/"),
            ("Try Gentle Breathing", "/suggestions/breathing-exercises/")
        ]
    },

    "anxiety": {
        "suggestions": [
            ("Do Deep Breathing", "/suggestions/breathing-exercises/"),
            ("Try Grounding Meditation", "/suggestions/meditation/"),
            ("Stretch or Do Yoga", "/dashboard/"),
            ("Vent Anonymously", "/community/")
        ]
    },

    "stress": {
        "suggestions": [
            ("Try Breathing Exercise", "/suggestions/breathing-exercises/"),
            ("Play a Stress-Relief Game", "/suggestions/game/1/"),
            ("Take a Meditation Break", "/suggestions/meditation/"),
            ("Talk to the Community", "/community/")
        ]
    },

    "overwhelmed": {
        "suggestions": [
            ("Breathe Through the Moment", "/suggestions/breathing-exercises/"),
            ("Guided Meditation for Overwhelm", "/suggestions/meditation/"),
            ("Affirm Your Efforts", "/suggestions/self-affirmation/1/"),
            ("Reach Out to Someone", "/community/")
        ]
    },

    "calm": {
        "suggestions": [
            ("Set a New Personal Goal", "/goals/"),
            ("Maintain Your Calm with Meditation", "/suggestions/meditation/"),
            ("Do Light Yoga", "/dashboard/"),
            ("Encourage Others", "/community/")
        ]
    },

    "hopeful": {
        "suggestions": [
            ("Work Toward a Goal", "/goals/"),
            ("Inspire Others", "/community/"),
            ("Reflect with Affirmations", "/suggestions/self-affirmation/1/"),
            ("Channel Your Hope with Meditation", "/suggestions/meditation/")
        ]
    },

    "happy": {
        "suggestions": [
            ("Celebrate a Goal", "/goals/"),
            ("Motivate Someone", "/community/"),
            ("Reflect on Positivity", "/suggestions/self-affirmation/1/"),
            ("Share Joy", "/community/")
        ]
    }
}


import random
# View to save and analyze journal entry
@login_required
def analyze_journal_entry(request):
    if request.method == "POST":
        journal_text = request.POST.get("journal_entry", "").strip()

        if journal_text:
            # Get mental health prediction
            prediction = predict_mental_health(journal_text)

            # Get sentiment analysis
            sentiment = analyze_sentiment(journal_text)

            # Save the journal entry with prediction and sentiment
            entry = JournalEntry.objects.create(user=request.user, text=journal_text, mental_health_status=prediction, sentiment=sentiment)

            entries = JournalEntry.objects.filter(user=request.user).order_by("-created_at")
            grouped_entries = defaultdict(list)
            for entry in entries:
                grouped_entries[entry.created_at.date()].append(entry)
            status_key = sentiment.lower() if prediction.lower() == "normal" else prediction.lower()
            suggestion_set = SUGGESTIONS_BY_STATUS.get(status_key, {})
            suggestions = suggestion_set.get("suggestions", [])
            random_suggestions = random.sample(suggestions, min(4, len(suggestions))) if suggestions else []

            helpline_info = suggestion_set.get("helplines", []) if status_key == "suicidal" else []
            return render(request, "core/dashboard.html", {
                "entries": dict(grouped_entries),
                "random_suggestions": random_suggestions,
                "helpline_info": helpline_info,
            })
    return redirect("dashboard")  # Redirect back to dashboard

def assign_daily_goals(user):
    """Assigns 3 random goals to a user for the current day if not already assigned."""
    today = date.today()
    if not DailyGoal.objects.filter(user=user, date=today).exists():
        goals = Goal.objects.order_by('?')[:3]  # Get 3 random goals
        for goal in goals:
            DailyGoal.objects.create(user=user, goal=goal, date=today, completed=False)

@login_required
def complete_goal(request, goal_id):
    try:
        goal = DailyGoal.objects.get(id=goal_id, user=request.user)
        goal.completed = True
        goal.save()
        return JsonResponse({"status": "success"})
    except DailyGoal.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Goal not found"}, status=404)

@login_required
def complete_personal_goal(request, goal_id):
    try:
        print(f"Received request to complete goal ID: {goal_id} by user: {request.user}")  # Debugging
        goal = PersonalGoal.objects.get(id=goal_id, user=request.user)
        goal.completed = True
        goal.save()
        print(f"Goal {goal_id} marked as completed!")  # Debugging
        return JsonResponse({"status": "success"})
    except PersonalGoal.DoesNotExist:
        print(f"Goal {goal_id} not found or doesn't belong to user {request.user}")  # Debugging
        return JsonResponse({"status": "error", "message": "Goal not found"}, status=404)

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt  # TEMPORARY: Only use for debugging. Remove later!
def delete_personal_goal(request, goal_id):
    if request.method == "POST":
        goal = get_object_or_404(PersonalGoal, id=goal_id, user=request.user)
        goal.delete()
        return JsonResponse({"status": "success", "message": "Goal deleted successfully!"})
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")
    unread_count = notifications.filter(is_read=False).count()  # Count unread notifications
    return render(request, "core/notification.html", {
        "notifications": notifications,
        "unread_count": unread_count,
    })

from .models import Notification


def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect("notifications")  # Redirect back to the notifications page
@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    return redirect('notifications')  # Replace with your actual notifications URL name
@login_required
def mark_all_notifications_as_read(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    notifications.update(is_read=True)  # ✅ Bulk update all unread notifications
    return redirect("notifications")  # Redirect back to the notifications page