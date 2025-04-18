from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import MeditationForm, YogaSessionForm
from django.utils import timezone
from datetime import date
from django.utils.timezone import now, localdate
from django.contrib import messages
from django.http import JsonResponse
from .models import BubbleGameRecord, MemoryGameScore, YogaSession, YogaCompletion, FocusMazeScore,Meditation, UserMeditation, SelfAffirmation
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Min
@login_required
def self_affirmation_step(request, step=1):

    questions = {
        1: ("What are three best things you've accomplished in the past few days?", "accomplishments"),
        2: ("What are three things you love about yourself?", "strengths"),
        3: ("What's a positive message you would tell yourself?", "positive_message"),
    }

    if step not in questions:
        return redirect("self_affirmation_complete")

    question, field_name = questions[step]
    step_percent = (step - 1) * 33

    # Initialize or fetch from session
    if step == 1 and request.method == "GET":
        request.session['affirmation_data'] = {}

    # Handle POST for current step
    if request.method == "POST":
        response = request.POST.get("response", "").strip()
        if response:
            data = request.session.get("affirmation_data", {})
            data[field_name] = response
            request.session["affirmation_data"] = data

            if step == 3:
                # Save new SelfAffirmation instance to DB
                data = request.session.pop("affirmation_data", {})
                SelfAffirmation.objects.create(
                    user=request.user,
                    date=timezone.localdate(),
                    accomplishments=data.get("accomplishments", ""),
                    strengths=data.get("strengths", ""),
                    positive_message=data.get("positive_message", "")
                )
                return redirect("self_affirmation_complete")
            else:
                return redirect("self_affirmation_step", step=step + 1)

    encouragement_messages = [
        "You're doing great! Keep reflecting on your journey. 😊",
        "Be kind to yourself—you're amazing just as you are! 💙",
        "Self-awareness is powerful. Keep going! ✨"
    ]

    return render(request, "suggestions/self_affirmation_step.html", {
        "step": step,
        "step_percent": step_percent,
        "question": question,
        "encouragement": encouragement_messages[step - 1],
        "is_complete": False,
    })

@login_required
def self_affirmation_complete(request):
    return render(request, "suggestions/self_affirmation_complete.html")


def breathing_exercises(request):
    return render(request, 'suggestions/breathing_exercises.html')
def meditation(request):
    return render(request, 'suggestions/meditation.html')
def breathing_circle(request):
    return render(request, 'suggestions/breathing_circle.html')
def breathing_478(request):
    return render(request, 'suggestions/breathing_478.html')
def breathing_711(request):
    return render(request, 'suggestions/breathing_711.html')
def breathing_box(request):
    return render(request, 'suggestions/breathing_box.html')
from django.shortcuts import render

# Define the story as a list of scenes with choices
STORY = {
    1: {
        'title': 'Waking Up in a Garden',
        'description': 'You wake up in a peaceful garden. The sun is shining, and birds are singing. You\'re not sure how you got here, but it feels safe and serene.',
        'choices': [
            {'text': 'Explore the garden', 'next_scene': 2},
            {'text': 'Sit by the pond and relax', 'next_scene': 3},
        ]
    },
    2: {
        'title': 'Exploring the Garden',
        'description': 'As you walk through the garden, you find a beautiful flower that glows softly in the sunlight. There is a path that leads to a cozy gazebo.',
        'choices': [
            {'text': 'Pick the flower', 'next_scene': 4},
            {'text': 'Walk to the gazebo', 'next_scene': 5},
        ]
    },
    3: {
        'title': 'Sitting by the Pond',
        'description': 'You sit by the peaceful pond, feeling the soft breeze and hearing the gentle rustle of leaves. It feels like the world has slowed down.',
        'choices': [
            {'text': 'Close your eyes and meditate', 'next_scene': 6},
            {'text': 'Look at the view and breathe deeply', 'next_scene': 7},
        ]
    },
    4: {
        'title': 'Picking the Flower',
        'description': 'You pick the glowing flower, and its scent fills the air. You feel calm and relaxed as the peaceful energy washes over you.',
        'choices': [
            {'text': 'Sit and enjoy the view', 'next_scene': 8},
            {'text': 'Continue walking to the gazebo', 'next_scene': 5},
        ]
    },
    5: {
        'title': 'Walking to the Gazebo',
        'description': 'You walk to the gazebo, surrounded by soft cushions and a view of the serene garden. It feels like the perfect place to relax.',
        'choices': [
            {'text': 'Sit and relax', 'next_scene': 6},
            {'text': 'Look at the view and breathe deeply', 'next_scene': 7},
        ]
    },
    6: {
        'title': 'Meditating in the Gazebo',
        'description': 'You close your eyes, breathe deeply, and feel your body relax with each breath. The sounds around you are soothing, and you feel at peace.',
        'choices': [
            {'text': 'Sit and enjoy the tranquility', 'next_scene': 8},
            {'text': 'Explore more of the garden', 'next_scene': 2},
        ]
    },
    7: {
        'title': 'Looking at the View',
        'description': 'You sit and take in the breathtaking view of the garden. You breathe in the fresh air, feeling all your tension melt away.',
        'choices': [
            {'text': 'Sit and enjoy the view more', 'next_scene': 8},
            {'text': 'Close your eyes and meditate', 'next_scene': 6},
        ]
    },
    8: {
        'title': 'Enjoying the Serenity',
        'description': 'You sit quietly and enjoy the serenity of the garden. The peace and calm have settled deep within you, leaving you feeling relaxed and refreshed.',
        'choices': [
            {'text': 'Take a deep breath and feel the calmness', 'next_scene': 8},
            {'text': 'Exit the garden and continue on with your day', 'next_scene': None},
        ]
    }
}
def game(request, scene_id):
    # Retrieve the scene from STORY using scene_id
    current_scene = STORY.get(scene_id)

    # If the scene exists, render it normally
    if current_scene:
        choices = current_scene['choices']
        return render(request, 'suggestions/distractiongame.html', {
            'scene': current_scene,
            'choices': choices
        })
    
    # If the scene doesn't exist (which ideally shouldn't happen), fall back to the final peaceful scene
    final_scene = STORY[8]  # Always render the peaceful final scene
    return render(request, 'suggestions/distractiongame.html', {
        'scene': final_scene,
        'choices': final_scene['choices']
    })

@login_required
def meditation_list(request):
    meditations = Meditation.objects.all()
    today = localdate()

    # Get only today's completed meditations
    user_completed_meditations = UserMeditation.objects.filter(
        user=request.user, completed_at__date=today
    ).values_list('meditation_id', flat=True)

    return render(request, 'suggestions/meditation_list.html', {
        'meditations': meditations,
        'user_completed_meditations': user_completed_meditations
    })

@login_required
def complete_meditation(request, meditation_id):
    meditation = get_object_or_404(Meditation, id=meditation_id)
    
    # Check if user has already completed it today
    today = localdate()
    already_completed = UserMeditation.objects.filter(
        user=request.user, meditation=meditation, completed_at__date=today
    ).exists()

    if already_completed:
        messages.info(request, f'You have already completed "{meditation.title}" today!')
    else:
        UserMeditation.objects.create(user=request.user, meditation=meditation)
        messages.success(request, f'You have completed "{meditation.title}"!')

    return redirect('meditation_list')  # Redirect back to the list
# Helper function to check if user is admin
def is_admin(user):
    return user.is_staff
# Helper function to check if user is an admin or a professional
def can_manage_meditations(user):
    return user.is_staff or getattr(user, 'is_professional', False)  # Ensure 'is_professional' exists
# Admin Panel to Manage Meditations
@user_passes_test(can_manage_meditations)
def manage_meditations(request):
    meditations = Meditation.objects.all()
    return render(request, 'users/manage_meditations.html', {'meditations': meditations})

# Add New Meditation
@user_passes_test(can_manage_meditations)
def add_meditation(request):
    if request.method == 'POST':
        form = MeditationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Meditation added successfully!")
            return redirect('manage_meditations')
    else:
        form = MeditationForm()
    return render(request, 'users/add_edit_meditation.html', {'form': form, 'action': 'Add'})

# Edit Meditation
@user_passes_test(can_manage_meditations)
def edit_meditation(request, meditation_id):
    meditation = get_object_or_404(Meditation, id=meditation_id)
    if request.method == 'POST':
        form = MeditationForm(request.POST, request.FILES, instance=meditation)
        if form.is_valid():
            form.save()
            messages.success(request, "Meditation updated successfully!")
            return redirect('manage_meditations')
    else:
        form = MeditationForm(instance=meditation)
    return render(request, 'users/add_edit_meditation.html', {'form': form, 'action': 'Edit'})

# Delete Meditation
@user_passes_test(can_manage_meditations)
def delete_meditation(request, meditation_id):
    meditation = get_object_or_404(Meditation, id=meditation_id)
    meditation.delete()
    messages.success(request, "Meditation deleted successfully!")
    return redirect('manage_meditations')
# Helper function to check if user is an admin or a professional
def can_manage_yoga(user):
    return user.is_staff or getattr(user, 'is_professional', False)

# Admin/Professional Panel to Manage Yoga Sessions
@user_passes_test(can_manage_yoga)
def manage_yoga_sessions(request):
    sessions = YogaSession.objects.all()
    return render(request, 'users/manage_yoga.html', {'sessions': sessions})

# Add New Yoga Session
@user_passes_test(can_manage_yoga)
def add_yoga_session(request):
    if request.method == 'POST':
        form = YogaSessionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Yoga session added successfully!")
            return redirect('manage_yoga')
    else:
        form = YogaSessionForm()
    return render(request, 'users/add_edit_yoga.html', {'form': form, 'action': 'Add'})

# Edit Yoga Session
@user_passes_test(can_manage_yoga)
def edit_yoga_session(request, session_id):
    session = get_object_or_404(YogaSession, id=session_id)
    if request.method == 'POST':
        form = YogaSessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, "Yoga session updated successfully!")
            return redirect('manage_yoga')
    else:
        form = YogaSessionForm(instance=session)
    return render(request, 'users/add_edit_yoga.html', {'form': form, 'action': 'Edit'})

# Delete Yoga Session
@user_passes_test(can_manage_yoga)
def delete_yoga_session(request, session_id):
    session = get_object_or_404(YogaSession, id=session_id)
    session.delete()
    messages.success(request, "Yoga session deleted successfully!")
    return redirect('manage_yoga')

@login_required
def relaxation_games_home(request):
    return render(request, 'suggestions/relaxation_games_home.html')
@login_required
def bubble_pop_game(request):
    high_score = BubbleGameRecord.objects.filter(user=request.user).first()
    return render(request, 'suggestions/bubble_pop.html', {
       'high_score': high_score.score if high_score else 0 
    })

@login_required
def save_bubble_score(request):
    if request.method == "POST":
        score = int(request.POST.get("score", 0))
        if score > 0:
            BubbleGameRecord.objects.create(user=request.user, score=score)
        return JsonResponse({"message": "Score saved!"})
    return JsonResponse({"error": "Invalid request"}, status=400)
@login_required
def memory_game_view(request):
    best_time = None
    best_attempts = None

    if request.user.is_authenticated:
        best_score = MemoryGameScore.objects.filter(user=request.user, score=8).order_by('time_taken').first()
        if best_score:
            best_time = best_score.time_taken
            best_attempts = best_score.attempts

    return render(request, 'suggestions/memory_game.html', {
        'best_time': best_time,
        'best_attempts': best_attempts
    })

@login_required
@csrf_exempt
def save_memory_score(request):
    if request.method == 'POST' and request.user.is_authenticated:
        score = int(request.POST.get('score', 0))
        time_taken = int(request.POST.get('time_taken', 0))
        attempts = int(request.POST.get('attempts', 0))

        # Save the new score
        MemoryGameScore.objects.create(
            user=request.user,
            score=score,
            time_taken=time_taken,
            attempts=attempts
        )

        # Get best score for user (only if all matches found i.e. score == 8)
        best_score = MemoryGameScore.objects.filter(user=request.user, score=8).order_by('time_taken').first()

        return JsonResponse({
            'message': 'Score saved successfully!',
            'best_time': best_score.time_taken if best_score else None,
            'best_attempts': best_score.attempts if best_score else None
        })
    
    return JsonResponse({'message': 'Failed to save score.'}, status=400)
def focus_maze(request):
    high_score = None
    if request.user.is_authenticated:
        best = FocusMazeScore.objects.filter(user=request.user).aggregate(Min('time_taken'))
        high_score = best['time_taken__min']
    return render(request, 'suggestions/focus_maze.html',{
        'high_score': high_score,
    })
@csrf_exempt
def save_focus_maze_score(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        time_taken = data.get('time_taken')

        if time_taken is not None:
            FocusMazeScore.objects.create(user=request.user, time_taken=time_taken)
            # get new best time
            best = FocusMazeScore.objects.filter(user=request.user).aggregate(Min('time_taken'))
            return JsonResponse({'status': 'success', 'new_high': best['time_taken__min']}, status=201)

    return JsonResponse({'status': 'error'}, status=400)
def four_in_a_row_view(request):
    return render(request, 'suggestions/four_in_a_row.html')

def yoga(request):
    sessions = YogaSession.objects.all()
    today = date.today()
    user_completed_yoga = YogaCompletion.objects.filter(
        user=request.user,
        completed_at__date=today
    ).values_list('session_id', flat=True)
    return render(request, 'suggestions/yoga_list.html', {
        'sessions': sessions,
        'user_completed_yoga': user_completed_yoga
    })

@login_required
def complete_yoga(request, session_id):
    session = get_object_or_404(YogaSession, id=session_id)
    YogaCompletion.objects.get_or_create(user=request.user, session=session)
    return redirect('yoga_home')  # You can customize the redirect as needed