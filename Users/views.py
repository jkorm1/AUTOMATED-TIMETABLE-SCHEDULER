from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from .forms import  CustomLoginForm
from .forms import CustomRegisterForm
from django.contrib.auth.decorators import login_required

from Users.models import StudentProfile, LecturerProfile
from django.contrib.auth.models import User
from django.contrib import messages


def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier')
        password = request.POST.get('password')
        is_student = request.POST.get('is_student') == 'True'

        try:
            if is_student:
                profile = StudentProfile.objects.get(index_number=identifier)
            else:
                profile = LecturerProfile.objects.get(staff_id=identifier)

            user = profile.user
            authenticated_user = authenticate(request, username=user.username, password=password)

            if authenticated_user:
                login(request, authenticated_user)
                return redirect('redirect_by_role')
            else:
                messages.error(request, "Incorrect password.")
        except (StudentProfile.DoesNotExist, LecturerProfile.DoesNotExist):
            messages.error(request, "Invalid credentials.")

    return render(request, 'users/login.html')

# Logout View
def logout_view(request):
    logout(request)
    return redirect('home')

# Role-based redirect
@login_required
def redirect_by_role(request):
    user = request.user
    if user.is_student and hasattr(user, 'studentprofile'):
        return redirect('portal:student_dashboard')
    elif user.is_lecturer and hasattr(user, 'lecturerprofile'):
        return redirect('portal:lecturer_dashboard')
    return redirect('home')

# Register View
def register_view(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])

            if form.cleaned_data['is_student']:
                user.is_student = True
            elif form.cleaned_data['is_lecturer']:
                user.is_lecturer = True

            user.save()

            if user.is_student:
                StudentProfile.objects.create(
                    user=user,
                    index_number=form.cleaned_data['index_number'],
                    program=form.cleaned_data['program'],
                    level=form.cleaned_data['level'],
                    secondary_email=form.cleaned_data['secondary_email']
                )
            elif user.is_lecturer:
                LecturerProfile.objects.create(
                    user=user,
                    staff_id=form.cleaned_data['staff_id'],
                    department=form.cleaned_data['department'],
                    secondary_email=form.cleaned_data['secondary_email']
                )

            return redirect('login')
    else:
        form = CustomRegisterForm()
    return render(request, 'users/register.html', {'form': form})

