from django.shortcuts import render,HttpResponse,redirect
from django.shortcuts import get_object_or_404
from .models import Room,Class,Lecturer,Course




# Create your views here.
def timetable(request):
    return HttpResponse('Test')

def rooms(request):
    rooms = Room.objects.all()
    
    if request.method == 'POST':
        department_building = request.POST.get('department_building')
        capacity = request.POST.get('capacity')
        room_code = request.POST.get('room_code')
        room_type = request.POST.get('room_type')

        if all([department_building, capacity, room_code, room_type]):
            Room.objects.create(
                department_building=department_building,
                capacity=capacity,
                room_code=room_code,
                room_type=room_type
            )
            return redirect('rooms')  

    return render(request, 'timetable/rooms.html', {'rooms': rooms})

def edit_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == 'POST':
        room.department_building = request.POST.get('department_building')
        room.capacity = request.POST.get('capacity')
        room.room_code = request.POST.get('room_code')
        room.room_type = request.POST.get('room_type')
        room.save()
        return redirect('rooms')

    return render(request, 'timetable/edit_room.html', {'room': room})

def delete_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    room.delete()
    return redirect('rooms')


def courses(request):
    courses = Course.objects.all()
    all_lecturers = Lecturer.objects.all()
    all_classes = Class.objects.all()
    all_courses = Course.objects.all()

    if request.method == 'POST':
        course_code = request.POST.get('course_code')
        course_title = request.POST.get('course_title')
        credit_hours = request.POST.get('credit_hours')
        department = request.POST.get('department')
        students_enrolled = request.POST.get('students_enrolled')

        course = Course.objects.create(
            course_code=course_code,
            course_title=course_title,
            credit_hours=credit_hours,
            department=department,
            students_enrolled=students_enrolled
        )

        # Set relationships
        course.lecturers.set(request.POST.getlist('lecturers'))
        course.classes.set(request.POST.getlist('classes'))
        course.course_prerequisites.set(request.POST.getlist('course_prerequisites'))

        return redirect('courses')

    return render(request, 'timetable/courses.html', {
        'courses': courses,
        'all_lecturers': all_lecturers,
        'all_classes': all_classes,
        'all_courses': all_courses
    })

def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    all_lecturers = Lecturer.objects.all()
    all_classes = Class.objects.all()
    all_courses = Course.objects.exclude(id=course_id)

    if request.method == 'POST':
        course.course_code = request.POST.get('course_code')
        course.course_title = request.POST.get('course_title')
        course.credit_hours = request.POST.get('credit_hours')
        course.department = request.POST.get('department')
        course.students_enrolled = request.POST.get('students_enrolled')
        course.save()

        course.lecturers.set(request.POST.getlist('lecturers'))
        course.classes.set(request.POST.getlist('classes'))
        course.course_prerequisites.set(request.POST.getlist('course_prerequisites'))

        return redirect('courses')

    return render(request, 'timetable/edit_course.html', {
        'course': course,
        'all_lecturers': all_lecturers,
        'all_classes': all_classes,
        'all_courses': all_courses
    })

def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    return redirect('courses')



import json

def lecturers(request):
    lecturers = Lecturer.objects.all()
    all_courses = Course.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        department = request.POST.get('department')
        office_location = request.POST.get('office_location')
        max_courses = request.POST.get('max_courses') or 4
        availability_raw = request.POST.get('availability')
        is_active = True if request.POST.get('is_active') == 'on' else False

        availability = None
        if availability_raw:
            try:
                availability = json.loads(availability_raw)
            except json.JSONDecodeError:
                availability = {"note": availability_raw}

        lecturer = Lecturer.objects.create(
            name=name,
            department=department,
            office_location=office_location,
            max_courses=max_courses,
            availability=availability,
            is_active=is_active
        )

        selected_courses = request.POST.getlist('courses')
        if selected_courses:
            lecturer.courses.set(selected_courses)

        return redirect('lecturers')

    return render(request, 'timetable/lecturers.html', {
        'lecturers': lecturers,
        'all_courses': all_courses
    })


def edit_lecturer(request, lecturer_id):
    lecturer = get_object_or_404(Lecturer, id=lecturer_id)
    all_courses = Course.objects.all()

    if request.method == 'POST':
        lecturer.name = request.POST.get('name')
        lecturer.department = request.POST.get('department')
        lecturer.office_location = request.POST.get('office_location')
        lecturer.max_courses = request.POST.get('max_courses') or 4
        lecturer.is_active = True if request.POST.get('is_active') == 'on' else False

        availability_raw = request.POST.get('availability')
        if availability_raw:
            try:
                lecturer.availability = json.loads(availability_raw)
            except json.JSONDecodeError:
                lecturer.availability = {"note": availability_raw}
        else:
            lecturer.availability = None

        lecturer.save()

        selected_courses = request.POST.getlist('courses')
        lecturer.courses.set(selected_courses)

        return redirect('lecturers')

    return render(request, 'timetable/edit_lecturer.html', {
        'lecturer': lecturer,
        'all_courses': all_courses
    })



def delete_lecturer(request, lecturer_id):
    lecturer = get_object_or_404(Lecturer, id=lecturer_id)
    lecturer.delete()
    return redirect('lecturers')


def classes(request):
    classes = Class.objects.all()

    if request.method == 'POST':
        class_code = request.POST.get('class_code')
        level = request.POST.get('level')
        department = request.POST.get('department')
        college = request.POST.get('college')
        class_size = request.POST.get('class_size')

        if all([class_code, department, college, class_size]):
            Class.objects.create(
                class_code=class_code,
                level = level,
                department=department,
                college=college,
                class_size=class_size
            )
            return redirect('classes')  
        

    return render(request, 'timetable/classes.html', {'classes': classes})

def edit_class(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)

    if request.method == 'POST':
        class_obj.class_code = request.POST.get('class_code')
        class_obj.level = request.POST.get('level')
        class_obj.department = request.POST.get('department')
        class_obj.college = request.POST.get('college')
        class_obj.class_size = request.POST.get('class_size')
        class_obj.save()
        return redirect('classes')

    return render(request, 'timetable/edit_class.html', {'class': class_obj})

def delete_class(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    class_obj.delete()
    return redirect('classes')




