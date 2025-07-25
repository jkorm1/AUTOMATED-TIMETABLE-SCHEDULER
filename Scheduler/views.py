from django.shortcuts import render, redirect, get_object_or_404
from .algorithm import run_genetic_algorithm
from Timetable.models import Class, Room, Course, Lecturer, College, Department, LectureSchedule
from collections import defaultdict
from django.contrib import messages
from django.http import Http404


def generate(request):
    colleges = College.objects.all()
    selected_college = None
    timetable = None
    # Build timetable status for each college
    college_timetable_status = {}
    for college in colleges:
        class_ids = list(Class.objects.filter(department__college=college).values_list('id', flat=True))
        has_timetable = LectureSchedule.objects.filter(program_class_id__in=class_ids).exists()
        college_timetable_status[college.id] = has_timetable
    if request.method == 'POST':
        if 'accept' in request.POST:
            # Accept and save timetable
            timetable = request.session.get('timetable_preview')
            college_id = request.session.get('selected_college_id')
            if timetable and college_id:
                selected_college = College.objects.get(id=college_id)
                class_ids = list(Class.objects.filter(department__college=selected_college).values_list('id', flat=True))
                LectureSchedule.objects.filter(program_class_id__in=class_ids).delete()
                for entry in timetable:
                    # Map codes/names to IDs
                    course_obj = Course.objects.get(code=entry['course'])
                    department = course_obj.department
                    # Find the class for this course's department
                    class_obj = Class.objects.filter(department=department).first()
                    if not class_obj:
                        print(f"Warning: No class found in department {department} for course {entry['course']}")
                        continue  # Skip this entry to avoid IntegrityError
                    # Find lecturer by name and department
                    lecturer_obj = Lecturer.objects.filter(name=entry['lecturer'], department=department).first()
                    if not lecturer_obj:
                        print(f"Warning: No lecturer found for name {entry['lecturer']} in department {department}")
                        continue  # Skip this entry to avoid IntegrityError
                    room_obj = Room.objects.get(code=entry['room'])
                    LectureSchedule.objects.create(
                        day=entry['day'],
                        period=entry['period'],
                        course_id=course_obj.id,
                        program_class_id=class_obj.id,
                        lecturer_id=lecturer_obj.id,
                        room_id=room_obj.id,
                    )
                messages.success(request, f"Timetable for {selected_college.name} accepted and saved.")
                # Clear session
                del request.session['timetable_preview']
                del request.session['selected_college_id']
                return redirect('generate')
            else:
                messages.error(request, "No timetable to accept.")
                return redirect('generate')
        else:
            # Run scheduler and preview timetable
            college_id = request.POST.get('college_id')
            if college_id:
                selected_college = College.objects.get(id=college_id)
                # Check if timetable exists for this college
                class_ids = list(Class.objects.filter(department__college=selected_college).values_list('id', flat=True))
                has_timetable = LectureSchedule.objects.filter(program_class_id__in=class_ids).exists()
                if has_timetable:
                    messages.warning(request, f"A timetable already exists for {selected_college.name}. Generating a new timetable will override the existing one.")
                departments = Department.objects.filter(college=selected_college)
                classes = list(Class.objects.filter(department__in=departments).values_list('code', flat=True))
                class_size = {item['code']: item['size'] for item in Class.objects.filter(department__in=departments).values('code', 'size')}
                courses = list(Course.objects.filter(department__in=departments).values_list('code', flat=True))
                course_credit_hours = {item['code']: item['credit_hours'] for item in Course.objects.filter(department__in=departments).values('code', 'credit_hours')}
                student_enrollment = {item['code']: item['enrollment'] for item in Course.objects.filter(department__in=departments).values('code', 'enrollment')}
                lecturers = list(Lecturer.objects.filter(department__in=departments).values_list('name', flat=True))
                lecturers_courses_mapping = defaultdict(list)
                for course in Course.objects.filter(department__in=departments).prefetch_related('lecturers').all():
                    for lecturer in course.lecturers.all():
                        lecturers_courses_mapping[course.code].append(lecturer.name)
            else:
                selected_college = None
                classes = list(Class.objects.values_list('code', flat=True))
                class_size = {item['code']: item['size'] for item in Class.objects.values('code', 'size')}
                courses = list(Course.objects.values_list('code', flat=True))
                course_credit_hours = {item['code']: item['credit_hours'] for item in Course.objects.values('code', 'credit_hours')}
                student_enrollment = {item['code']: item['enrollment'] for item in Course.objects.values('code', 'enrollment')}
                lecturers = list(Lecturer.objects.values_list('name', flat=True))
                lecturers_courses_mapping = defaultdict(list)
                for course in Course.objects.prefetch_related('lecturers').all():
                    for lecturer in course.lecturers.all():
                        lecturers_courses_mapping[course.code].append(lecturer.name)
            rooms = list(Room.objects.values_list('code', flat=True))
            room_size = {item['code']: item['capacity'] for item in Room.objects.values('code', 'capacity')}
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        lecture_hours = [
            '8:00 - 8:55', '9:00 - 9:55', '10:30 - 11:25', '11:30 - 12:25',
            '13:00 - 13:55', '14:00 - 14:55', '15:00 - 15:55',
            '16:00 - 16:55', '17:00 - 17:55', '18:00 - 18:55'
        ]
        lecturer_availability = {}
        for item in Lecturer.objects.values('name', 'availability'):
            availability = item['availability']
            if isinstance(availability, dict):  
                lecturer_availability[item['name']] = availability
            else:
                lecturer_availability[item['name']] = {}
        best_schedule = run_genetic_algorithm(
            class_size=class_size,
            rooms=rooms,
            room_size=room_size,
            days=days,
            lecture_hours=lecture_hours,
            courses=courses,
            course_credit_hours=course_credit_hours,
            student_enrollment=student_enrollment,
            lecturers=lecturers,
            lecturers_courses_mapping=lecturers_courses_mapping,
            lecturer_availability=lecturer_availability,
        )
        # Store in session for acceptance
        request.session['timetable_preview'] = best_schedule
        request.session['selected_college_id'] = college_id
        return render(request, 'scheduler/generate.html', {
            'best_schedule': best_schedule,
            'colleges': colleges,
            'selected_college': selected_college,
            'accept_mode': True,
        })
    # End of POST branch
    else:
        # GET: show form
         return render(request, 'scheduler/generate_schedule.html', {'colleges': colleges, 'college_timetable_status': college_timetable_status})


def college_timetable(request, college_id):
    try:
        college = College.objects.get(id=college_id)
    except College.DoesNotExist:
        raise Http404("College not found")
    colleges = College.objects.all()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    periods = [
        '8:00 - 8:55', '9:00 - 9:55', '10:30 - 11:25', '11:30 - 12:25',
        '13:00 - 13:55', '14:00 - 14:55', '15:00 - 15:55',
        '16:00 - 16:55', '17:00 - 17:55', '18:00 - 18:55'
    ]
    # Get all classes in the college
    class_ids = list(Class.objects.filter(department__college=college).values_list('id', flat=True))
    # Get all schedules for these classes
    schedules = LectureSchedule.objects.filter(program_class_id__in=class_ids)
    # Build grid: {day: {period: [entries]}}
    grid = {day: {period: [] for period in periods} for day in days}
    for sched in schedules:
        grid[sched.day][sched.period].append({
            'course': sched.course.code,
            'class': sched.program_class.code if sched.program_class else '',
            'lecturer': sched.lecturer.name if sched.lecturer else '',
            'room': sched.room.code if sched.room else '',
        })
    return render(request, 'scheduler/college_timetable.html', {
        'college': college,
        'colleges': colleges,
        'days': days,
        'periods': periods,
        'grid': grid,
    })