from django.shortcuts import render,HttpResponse
from .algorithm import run_genetic_algorithm
from Timetable.models import Class,Room,Course,Lecturer
from collections import defaultdict 
import json 
# Create your views here.
# def generate(request):
#     classes = list(Class.objects.values('class_code', flat = True))
#     class_size = {item['class_code']: item['class_size'] for item in Class.objects.values('class_code', 'class_size')}
#     rooms = list(Room.objects.values('room_code', flat = True))
#     room_size = {item['room_code']: item['capacity'] for item in Room.objects.values('room_code', 'capacity')}
#     days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
#     lecture_hours = ['8:00 - 8:55', '9:00 - 9:55', '10:30 - 11:25', '11:30 - 12:25', '13:00 - 13:55','14:00 - 14:55','15:00 - 15:55','16:00 - 16:55','17:00 - 17:55','18:00 - 18:55']
#     courses = list(Course.objects.values_list('course_code', flat=True))
#     course_credit_hours = {item['course_code']: item['credit_hours'] for item in Course.objects.values('course_code', 'credit_hours')}
#     student_enrollment = list(Course.objects.values_list('students_enrolled', flat=True))
#     course_prerequisites = {item['course_code']: item['course_prerequisites'] for item in Course.objects.values('course_code', 'course_prerequisites')}
#     lecturers = list(Lecturer.objects.values('name', flat = True))
#     lecturers_courses_mapping = {item['name']: item['courses'] for item in Lecturer.objects.values('name', 'courses')}
#     lecturer_availability = {item['name']: item['availability'] for item in Lecturer.objects.values('name', 'availability')}


#     best_schedule = run_genetic_algorithm(
#         class_size=class_size,
#         rooms=rooms,
#         room_size=room_size,
#         days=days,
#         lecture_hours=lecture_hours,
#         courses=courses,
#         course_credit_hours=course_credit_hours,
#         student_enrollment=student_enrollment,
#         course_prerequisites=course_prerequisites,
#         lecturers=lecturers,
#         lecturers_courses_mapping=lecturers_courses_mapping,
#         lecturer_availability=lecturer_availability,
#     )
#     return render(request, 'scheduler/generate.html',best_schedule)


def generate(request):
    # Class data
    classes = list(Class.objects.values_list('class_code', flat=True))
    class_size = {item['class_code']: item['class_size'] for item in Class.objects.values('class_code', 'class_size')}
    
    # Room data
    rooms = list(Room.objects.values_list('room_code', flat=True))
    room_size = {item['room_code']: item['capacity'] for item in Room.objects.values('room_code', 'capacity')}
    
    # Days and time slots
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    lecture_hours = [
        '8:00 - 8:55', '9:00 - 9:55', '10:30 - 11:25', '11:30 - 12:25',
        '13:00 - 13:55', '14:00 - 14:55', '15:00 - 15:55',
        '16:00 - 16:55', '17:00 - 17:55', '18:00 - 18:55'
    ]
    
    # Course data
    courses = list(Course.objects.values_list('course_code', flat=True))
    course_credit_hours = {item['course_code']: item['credit_hours'] for item in Course.objects.values('course_code', 'credit_hours')}
    student_enrollment = {item['course_code']: item['students_enrolled'] for item in Course.objects.values('course_code', 'students_enrolled')}
    
    # Prerequisites
    course_prerequisites = {
        course.course_code: [pr.course_code for pr in course.course_prerequisites.all()]
        for course in Course.objects.prefetch_related('course_prerequisites').all()
    }

    # Lecturer data
    lecturers = list(Lecturer.objects.values_list('name', flat=True))
    
    # Lecturer-course mapping
    lecturers_courses_mapping = defaultdict(list)
    for course in Course.objects.prefetch_related('lecturers').all():
        for lecturer in course.lecturers.all():
            lecturers_courses_mapping[course.course_code].append(lecturer.name)


    # Lecturer availability
    lecturer_availability = {}
    for item in Lecturer.objects.values('name', 'availability'):
        availability = item['availability']
        if isinstance(availability, dict):  
            lecturer_availability[item['name']] = availability
        else:
            lecturer_availability[item['name']] = {}  


    # Run the genetic algorithm
    best_schedule = run_genetic_algorithm(
        class_size=class_size,
        rooms=rooms,
        room_size=room_size,
        days=days,
        lecture_hours=lecture_hours,
        courses=courses,
        course_credit_hours=course_credit_hours,
        student_enrollment=student_enrollment,
        course_prerequisites=course_prerequisites,
        lecturers=lecturers,
        lecturers_courses_mapping=lecturers_courses_mapping,
        lecturer_availability=lecturer_availability,
    )

    return render(request, 'scheduler/generate.html', {'best_schedule': best_schedule})


def generate_schedule(request):
    return render(request, 'scheduler/generate_schedule.html')

# def generate(request):
#     # Classes
#     classes = list(Class.objects.values_list('class_code', flat=True))
#     class_size = {c.class_code: c.class_size for c in Class.objects.all()}

#     # Rooms
#     rooms = list(Room.objects.values_list('room_code', flat=True))
#     room_size = {r.room_code: r.capacity for r in Room.objects.all()}

#     # Days and Time Slots
#     days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
#     lecture_hours = [
#         '8:00 - 8:55', '9:00 - 9:55', '10:30 - 11:25', '11:30 - 12:25',
#         '13:00 - 13:55', '14:00 - 14:55', '15:00 - 15:55',
#         '16:00 - 16:55', '17:00 - 17:55', '18:00 - 18:55'
#     ]

#     # Courses and related data
#     courses = list(Course.objects.values_list('course_code', flat=True))
#     course_credit_hours = {c.course_code: c.credit_hours for c in Course.objects.all()}
#     student_enrollment = {c.course_code: c.students_enrolled for c in Course.objects.all()}
    
#     # Prerequisites
#     course_prerequisites = {
#         c.course_code: [p.course_code for p in c.course_prerequisites.all()]
#         for c in Course.objects.all()
#     }

#     # Lecturers and availability
#     lecturers = list(Lecturer.objects.values_list('name', flat=True))
#     lecturer_availability = {
#         l.name: l.availability for l in Lecturer.objects.all()
#     }

#     # Lecturer-course mapping (Many-to-Many)
#     lecturers_courses_mapping = {
#         l.name: [c.course_code for c in l.courses.all()]
#         for l in Lecturer.objects.all()
#     }

#     # You can now pass this data to your algorithm
#     best_schedule = run_genetic_algorithm(
#         class_size=class_size,
#         rooms=rooms,
#         room_size=room_size,
#         days=days,
#         lecture_hours=lecture_hours,
#         courses=courses,
#         course_credit_hours=course_credit_hours,
#         student_enrollment=student_enrollment,
#         course_prerequisites=course_prerequisites,
#         lecturers=lecturers,
#         lecturers_courses_mapping=lecturers_courses_mapping,
#         lecturer_availability=lecturer_availability,
#     )

#     return render(request, 'scheduler/generate.html', best_schedule)