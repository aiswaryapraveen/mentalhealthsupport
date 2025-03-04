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

@login_required
def dashboard(request):
    total_users = CustomUser.objects.count() if request.user.is_superuser else None
    total_professionals = CustomUser.objects.filter(is_professional=True).count() if request.user.is_superuser else None

    

    # Handle journal submission for normal users
    entries = None
    if not request.user.is_superuser and not request.user.is_professional:
        if request.method == "POST":
            journal_text = request.POST.get("journal_entry")
            if journal_text.strip():
                JournalEntry.objects.create(user=request.user, text=journal_text)
            return redirect("dashboard")  # Refresh after submission
        entries = JournalEntry.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "core/dashboard.html", {
        "entries": entries,
        "total_users": total_users,
        "total_professionals": total_professionals,
    })

