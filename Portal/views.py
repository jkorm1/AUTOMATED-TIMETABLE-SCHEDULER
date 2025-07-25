from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from Timetable.models import StudentProfile, LecturerProfile, Class, Lecturer, LectureSchedule

@login_required
def student_dashboard(request):
    try:
        student_profile = StudentProfile.objects.get(user=request.user)
        class_obj = student_profile.class_obj
        if not class_obj:
            return render(request, "portal/student_dashboard.html", {"error": "No class assigned."})
    except StudentProfile.DoesNotExist:
        return render(request, "portal/student_dashboard.html", {"error": "No student profile found."})
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    periods = [
        '8:00 - 8:55', '9:00 - 9:55', '10:30 - 11:25', '11:30 - 12:25',
        '13:00 - 13:55', '14:00 - 14:55', '15:00 - 15:55',
        '16:00 - 16:55', '17:00 - 17:55', '18:00 - 18:55'
    ]
    schedules = LectureSchedule.objects.filter(program_class=class_obj)
    grid = {day: {period: [] for period in periods} for day in days}
    for sched in schedules:
        grid[sched.day][sched.period].append({
            'course': sched.course.code,
            'lecturer': sched.lecturer.name if sched.lecturer else '',
            'room': sched.room.code if sched.room else '',
        })
    return render(request, "portal/student_dashboard.html", {
        "class_obj": class_obj,
        "days": days,
        "periods": periods,
        "grid": grid,
    })

@login_required
def lecturer_dashboard(request):
    try:
        lecturer_profile = LecturerProfile.objects.get(user=request.user)
        from Timetable.models import Lecturer
        lecturer = Lecturer.objects.filter(staff_id=lecturer_profile.staff_id).first()
        if not lecturer:
            return render(request, "portal/lecturer_dashboard.html", {"error": "No matching lecturer found for your staff ID."})
    except LecturerProfile.DoesNotExist:
        return render(request, "portal/lecturer_dashboard.html", {"error": "No lecturer profile found."})
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    periods = [
        '8:00 - 8:55', '9:00 - 9:55', '10:30 - 11:25', '11:30 - 12:25',
        '13:00 - 13:55', '14:00 - 14:55', '15:00 - 15:55',
        '16:00 - 16:55', '17:00 - 17:55', '18:00 - 18:55'
    ]
    from Timetable.models import LectureSchedule
    schedules = LectureSchedule.objects.filter(lecturer=lecturer)
    grid = {day: {period: [] for period in periods} for day in days}
    for sched in schedules:
        grid[sched.day][sched.period].append({
            'course': sched.course.code,
            'class': sched.program_class.code if sched.program_class else '',
            'room': sched.room.code if sched.room else '',
        })
    return render(request, "portal/lecturer_dashboard.html", {
        "lecturer": lecturer,
        "days": days,
        "periods": periods,
        "grid": grid,
    })

@login_required
def portal_profile(request):
    return HttpResponse("This is your profile page.")
