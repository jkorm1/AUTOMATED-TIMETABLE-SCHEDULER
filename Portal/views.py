from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

def student_dashboard(request):
    return render(request, "portal/student_dashboard.html")

def lecturer_dashboard(request):
    return render(request, "portal/lecturer_dashboard.html")

@login_required
def portal_profile(request):
    return HttpResponse("This is your profile page.")
