from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import SelfAffirmation

@login_required
def self_affirmation_step(request, step=1):
    """Handles multi-step self-affirmation questions."""
    
    # Calculate progress percentage
    if step == 1:
        step_percent = 0
    elif step == 2:
        step_percent = 33
    elif step == 3:
        step_percent = 66
    else:
        return redirect("self_affirmation_complete")

    if step == 1:
        question = "What are three best things you've accomplished in the past few days?"
        field_name = "accomplishments"
    elif step == 2:
        question = "What are three things you love about yourself?"
        field_name = "strengths"
    elif step == 3:
        question = "What's a positive message you would tell yourself?"
        field_name = "positive_message"
    else:
        return redirect("self_affirmation_complete")

    if request.method == "POST":
        response = request.POST.get("response", "").strip()
        if response:
            # Save or update the current response
            affirmation, created = SelfAffirmation.objects.get_or_create(
                user=request.user, date=request.POST.get("date")
            )
            setattr(affirmation, field_name, response)
            affirmation.save()

            # If this is the last step, display the completion message
            if step == 3:
                return render(request, "suggestions/self_affirmation_step.html", {
                    "step": step,
                    "step_percent": 100,  # Show 100% progress
                    "question": "Well done! 🎉",
                    "completion_message": "You've completed your self-affirmation reflection. Keep believing in yourself!",
                    "encouragement": "You're amazing just as you are! Keep shining and believing in yourself.",
                    "is_complete": True,  # To indicate completion
                })
            else:
                return redirect("self_affirmation_step", step=step + 1)

    encouragement_messages = [
        "You're doing great! Keep reflecting on your journey. 😊",
        "Be kind to yourself—you're amazing just as you are! 💙",
        "Self-awareness is powerful. Keep going! ✨"
    ]

    return render(request, "suggestions/self_affirmation_step.html", {
        "step": step,
        "step_percent": step_percent,  # Pass the calculated step_percent to the template
        "question": question,
        "encouragement": encouragement_messages[step - 1],
        "is_complete": False,
    })
from django.shortcuts import render

def breathing_exercises(request):
    return render(request, 'suggestions/breathing_exercises.html')
def breathing_circle(request):
    return render(request, 'suggestions/breathing_circle.html')
def breathing_478(request):
    return render(request, 'suggestions/breathing_478.html')
def breathing_711(request):
    return render(request, 'suggestions/breathing_711.html')
def breathing_box(request):
    return render(request, 'suggestions/breathing_box.html')
