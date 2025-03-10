from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from.models import JournalEntry
from users.models import Professional1
import os
from django.conf import settings

def landing_page(request):
    return render(request, 'core/landing.html')

def about_page(request):
    return render(request, 'core/about.html')

'''@login_required
def dashboard(request):
    if request.method == "POST":
        journal_text = request.POST.get("journal_entry")
        if journal_text.strip():  # Ensure non-empty input
            JournalEntry.objects.create(user=request.user, text=journal_text)
        return redirect("dashboard")  # Refresh page after submission
    entries = JournalEntry.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "core/dashboard.html", {"entries": entries})
'''

# @login_required
# def request_view(request):
#     # Check if the user is a superuser (optional for admin-only access)
#     if not request.user.is_superuser:
#         messages.error(request, "You are not authorized to view this page.")
#         return redirect('dashboard')

#     # Fetch all ProfessionalProfile records
#     profiles = Professional1.objects.all()

#     # Handle delete request if profile_id is provided
#     if request.method == 'POST' and 'delete' in request.POST:
#         profile_id = request.POST.get('profile_id')
#         profile = get_object_or_404(Professional1, id=profile_id)
#         profile.delete()
#         messages.success(request, f"Professional profile for {profile.user.username} has been deleted.")
#         return redirect('request_view')

#     if request.method == 'POST' and 'approve' in request.POST:
#         profile_id = request.POST.get('profile_id')
#         profile = get_object_or_404(Professional1, id=profile_id)

#         # Update the ProfessionalProfile and user type
#         profile.is_approved = True
#         profile.save()
#         profile.user.is_professional = True
#         profile.user.save()

#         messages.success(request, f"Professional profile for {profile.user.username} has been approved.")
#         return redirect('request_view')

#     if request.method == 'POST' and 'reject' in request.POST:
#         profile_id = request.POST.get('profile_id')
#         profile = get_object_or_404(Professional1, id=profile_id)
#         profile.is_approved = False
#         profile.save()

#         # Optionally set `is_professional` to False if rejecting an already approved profile
#         profile.user.is_professional = False
#         profile.user.save()

#         messages.success(request, f"Professional profile for {profile.user.username} has been rejected.")
#         return redirect('request_view')

#     return render(request, 'core/request.html', {'profiles': profiles})

import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.models import Professional1

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
                messages.success(request, f"Professional profile for {profile.user.username} has been rejected.")
                return redirect('request_view')

        return render(request, 'core/request.html', {'profiles': profiles})
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from users.models import CustomUser
from collections import defaultdict
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


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import JournalEntry
from textblob import TextBlob
import os
import re
import string
import pickle
import numpy as np
import tensorflow as tf
from django.conf import settings
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Load ML model and preprocessing tools
MODEL_PATH = os.path.join(settings.BASE_DIR, "core/ml_models/mental_health_model.h5")
TOKENIZER_PATH = os.path.join(settings.BASE_DIR, "core/ml_models/tokenizer.pkl")
ENCODER_PATH = os.path.join(settings.BASE_DIR, "core/ml_models/label_encoder.pkl")

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

# Function to analyze sentiment
def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    if sentiment > 0:
        return 'happy'
    elif sentiment < 0:
        return 'overwhelmed'
    else:
        return 'relaxed'

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

            # Render the dashboard with the updated journal entries
            return render(request, "core/dashboard.html", {
                "entries": dict(grouped_entries),
            })


    return redirect("dashboard")  # Redirect back to dashboard