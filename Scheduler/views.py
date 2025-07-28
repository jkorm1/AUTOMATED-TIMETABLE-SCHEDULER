from django.shortcuts import render, redirect, get_object_or_404
from .algorithm import run_genetic_algorithm
from Timetable.models import Class, Room, Course, Lecturer, College, Department, LectureSchedule
from collections import defaultdict
from django.contrib import messages
from django.http import Http404
from django.contrib.admin.views.decorators import staff_member_required
from Timetable.models import College, Department, Class, Course, Lecturer, Room, LectureSchedule, ExamDate, TimeSlot, ExamSchedule, InvigilationAssignment
from .algorithm import run_genetic_algorithm
from .exam_algorithm import run_exam_genetic_algorithm
from datetime import date
from collections import defaultdict


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


@staff_member_required
def generate_exam_schedule(request):
    """Generate exam schedule using genetic algorithm"""
    colleges = College.objects.all()
    selected_college = None
    exam_schedule = None
    exam_schedule_status = {}
    
    # Check existing exam schedules for each college
    for college in colleges:
        class_ids = list(Class.objects.filter(department__college=college).values_list('id', flat=True))
        has_exam_schedule = ExamSchedule.objects.filter(program_class_id__in=class_ids).exists()
        exam_schedule_status[college.id] = has_exam_schedule
    
    if request.method == 'POST':
        if 'accept' in request.POST:
            exam_schedule = request.session.get('exam_schedule_preview')
            college_id = request.session.get('selected_college_id')
            
            if exam_schedule and college_id:
                selected_college = College.objects.get(id=college_id)
                class_ids = list(Class.objects.filter(department__college=selected_college).values_list('id', flat=True))
                
                # Clear existing exam schedules for this college
                ExamSchedule.objects.filter(program_class_id__in=class_ids).delete()
                
                # Save new exam schedules
                for entry in exam_schedule:
                    course_obj = Course.objects.get(code=entry['course'])
                    class_obj = Class.objects.get(code=entry['class'])
                    room_obj = Room.objects.get(code=entry['room'])
                    
                    # Create or get exam date
                    from datetime import datetime
                    # Parse the date string back to a date object
                    date_obj = datetime.strptime(entry['date'], '%B %d, %Y').date()
                    exam_date_obj, created = ExamDate.objects.get_or_create(
                        date=date_obj,
                        defaults={'day_name': date_obj.strftime('%A')}
                    )
                    
                    # Create or get time slot
                    from datetime import time
                    # Parse the time strings back to time objects
                    start_time_obj = datetime.strptime(entry['start_time'], '%H:%M').time()
                    end_time_obj = datetime.strptime(entry['end_time'], '%H:%M').time()
                    time_slot_obj, created = TimeSlot.objects.get_or_create(
                        code=entry['time_slot'],
                        defaults={
                            'start_time': start_time_obj,
                            'end_time': end_time_obj,
                            'is_lecture_slot': False,
                            'is_exam_slot': True
                        }
                    )
                    
                    # Create exam schedule
                    exam_schedule_obj = ExamSchedule.objects.create(
                        exam_date=exam_date_obj,
                        time_slot=time_slot_obj,
                        course=course_obj,
                        program_class=class_obj,
                        room=room_obj,
                        exam_duration=entry['duration'],
                        is_scheduled=True
                    )
                    
                    # Assign invigilators
                    for i, invigilator_name in enumerate(entry['invigilators']):
                        invigilator_obj = Lecturer.objects.filter(name=invigilator_name).first()
                        if invigilator_obj:
                            role = 'CHIEF' if i == 0 else 'ASSISTANT'
                            InvigilationAssignment.objects.create(
                                exam_schedule=exam_schedule_obj,
                                invigilator=invigilator_obj,
                                role=role,
                                is_confirmed=False
                            )
                            exam_schedule_obj.invigilators.add(invigilator_obj)
                
                messages.success(request, f"Exam schedule for {selected_college.name} accepted and saved.")
                del request.session['exam_schedule_preview']
                del request.session['selected_college_id']
                return redirect('generate_exam_schedule')
            else:
                messages.error(request, "No exam schedule to accept.")
                return redirect('generate_exam_schedule')
        else:
            college_id = request.POST.get('college_id')
            exam_start_date = request.POST.get('exam_start_date')
            
            print(f"DEBUG: college_id = {college_id}")
            print(f"DEBUG: exam_start_date = {exam_start_date}")
            
            if college_id:
                selected_college = College.objects.get(id=college_id)
                class_ids = list(Class.objects.filter(department__college=selected_college).values_list('id', flat=True))
                
                # Check if exam schedule already exists
                has_exam_schedule = ExamSchedule.objects.filter(program_class_id__in=class_ids).exists()
                if has_exam_schedule:
                    messages.warning(request, f"An exam schedule already exists for {selected_college.name}. Generating a new schedule will override the existing one.")
                
                # Get data for the selected college (same approach as normal timetable)
                departments = Department.objects.filter(college=selected_college)
                classes = Class.objects.filter(department__in=departments)
                courses = Course.objects.filter(department__in=departments)
                invigilators = Lecturer.objects.filter(is_proctor=True, is_active=True)
                
                print(f"DEBUG: Found {departments.count()} departments")
                print(f"DEBUG: Found {classes.count()} classes")
                print(f"DEBUG: Found {courses.count()} courses")
                print(f"DEBUG: Found {invigilators.count()} invigilators")
                
                if not invigilators.exists():
                    messages.error(request, "No invigilators found. Please mark lecturers as proctors first.")
                    return render(request, 'scheduler/generate_exam_schedule.html', {
                        'colleges': colleges, 
                        'exam_schedule_status': exam_schedule_status,
                        'selected_college_id': college_id,
                        'selected_exam_start_date': exam_start_date,
                        'error': True
                    })
                
                # Get exam start date from form or use default (next Monday)
                if exam_start_date:
                    try:
                        start_date = date.fromisoformat(exam_start_date)
                    except ValueError:
                            messages.error(request, "Invalid date format. Please use YYYY-MM-DD format.")
                            return render(request, 'scheduler/generate_exam_schedule.html', {
                                'colleges': colleges, 
                                'exam_schedule_status': exam_schedule_status,
                                'selected_college_id': college_id,
                                'selected_exam_start_date': exam_start_date,
                                'error': True
                            })
                else:
                    # Default to next Monday
                    from datetime import timedelta
                    today = date.today()
                    days_until_monday = (7 - today.weekday()) % 7
                    start_date = today + timedelta(days=days_until_monday)
                
                # Prepare exam courses data (same approach as normal timetable)
                exam_courses = []
                print(f"DEBUG: Found {courses.count()} courses and {classes.count()} classes")
                
                # For exam scheduling, we'll assume courses in a department can be taken by classes in that department
                # This is the same assumption the normal timetable system makes
                for course in courses:
                    # Get classes in the same department as the course
                    course_classes = list(classes.filter(department=course.department))
                    
                    print(f"DEBUG: Course {course.code} (dept: {course.department.name}) can be taken by {len(course_classes)} classes")
                    
                    if course_classes:
                        exam_courses.append({
                            'course': course,
                            'classes': course_classes
                        })
                
                print(f"DEBUG: Total exam courses prepared: {len(exam_courses)}")
                
                if not exam_courses:
                    messages.error(request, f"No courses found for {selected_college.name}. Please ensure there are courses and classes in the departments of this college.")
                    return render(request, 'scheduler/generate_exam_schedule.html', {
                        'colleges': colleges, 
                        'exam_schedule_status': exam_schedule_status,
                        'selected_college_id': college_id,
                        'selected_exam_start_date': exam_start_date,
                        'error': True
                    })
                
                print(f"DEBUG: About to run genetic algorithm with {len(exam_courses)} courses")
                print(f"DEBUG: Start date: {start_date}")
                print(f"DEBUG: Invigilators count: {invigilators.count()}")
                
                # Run genetic algorithm for exam scheduling with automatic date/time generation
                try:
                    print("DEBUG: Calling run_exam_genetic_algorithm...")
                    best_exam_schedule = run_exam_genetic_algorithm(
                        exam_courses=exam_courses,
                        start_date=start_date,
                        invigilators=list(invigilators),
                        exam_duration_hours=2,
                        generations=50,
                        population_size=30
                    )
                    print(f"DEBUG: Genetic algorithm completed, got {len(best_exam_schedule)} exam sessions")
                    
                    if not best_exam_schedule:
                        print("DEBUG: No exam schedule generated!")
                        
                        # Calculate the issue
                        total_courses = len(exam_courses)
                        # Count unique classes across all courses
                        all_classes = set()
                        for course_data in exam_courses:
                            all_classes.update(course_data['classes'])
                        total_classes = len(all_classes)
                        total_sessions_needed = total_courses * 4  # Each course is taken by 4 classes
                        available_slots = 15 * 5  # 15 days × 5 slots
                        
                        error_message = f"""
                        No exam schedule could be generated for {selected_college.name}.
                        
                        Analysis:
                        - Courses found: {total_courses}
                        - Classes per course: {total_classes}
                        - Total exam sessions needed: {total_sessions_needed}
                        - Available slots: {available_slots} (15 days × 5 slots per day)
                        - Shortage: {total_sessions_needed - available_slots} slots
                        
                        Solutions:
                        1. Select a different college with fewer courses
                        2. Increase the exam period beyond 3 weeks
                        3. Add more time slots per day
                        4. Reduce the number of courses to be scheduled
                        """
                        
                        messages.error(request, error_message)
                        return render(request, 'scheduler/generate_exam_schedule.html', {
                            'colleges': colleges, 
                            'exam_schedule_status': exam_schedule_status,
                            'selected_college_id': college_id,
                            'selected_exam_start_date': exam_start_date,
                            'error': True
                        })
                        
                except Exception as e:
                    import traceback
                    print(f"DEBUG: Error in genetic algorithm: {e}")
                    print(f"DEBUG: Traceback: {traceback.format_exc()}")
                    messages.error(request, f"Error generating exam schedule: {str(e)}")
                    return render(request, 'scheduler/generate_exam_schedule.html', {
                        'colleges': colleges, 
                        'exam_schedule_status': exam_schedule_status,
                        'selected_college_id': college_id,
                        'selected_exam_start_date': exam_start_date,
                        'error': True
                    })
                
                # Convert to format suitable for template
                formatted_schedule = []
                for entry in best_exam_schedule:
                    formatted_schedule.append({
                        'course': entry['course'].code,
                        'class': entry['class'].code,
                        'date': entry['date'].strftime('%B %d, %Y'),  # Convert date to readable string
                        'time_slot': entry['time_slot']['code'],
                        'start_time': entry['time_slot']['start_time'].strftime('%H:%M'),  # Convert time to string
                        'end_time': entry['time_slot']['end_time'].strftime('%H:%M'),  # Convert time to string
                        'room': entry['room'].code,
                        'duration': entry['duration'],
                        'invigilators': [inv.name for inv in entry['invigilators']],
                        'required_invigilators': entry['required_invigilators'],
                        'week': entry['week']
                    })
                
                request.session['exam_schedule_preview'] = formatted_schedule
                request.session['selected_college_id'] = college_id
                
                return render(request, 'scheduler/generate_exam.html', {
                    'best_exam_schedule': formatted_schedule,
                    'colleges': colleges,
                    'selected_college': selected_college,
                    'accept_mode': True,
                })
            else:
                # No college selected
                messages.error(request, "Please select a college.")
                return render(request, 'scheduler/generate_exam_schedule.html', {
                    'colleges': colleges, 
                    'exam_schedule_status': exam_schedule_status,
                    'selected_exam_start_date': exam_start_date,
                    'error': True
                })
        
        return render(request, 'scheduler/generate_exam_schedule.html', {
            'colleges': colleges, 
            'exam_schedule_status': exam_schedule_status
        })
    else:
        return render(request, 'scheduler/generate_exam_schedule.html', {
            'colleges': colleges, 
            'exam_schedule_status': exam_schedule_status
        })