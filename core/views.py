from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def landing_page(request):
    return render(request, 'core/landing.html')

def about_page(request):
    return render(request, 'core/about.html')

@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')