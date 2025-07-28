from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('timetable/',views.timetable, name='timetable'),
    path('rooms/',views.rooms, name='rooms'),
    path('courses/', views.courses, name='courses'),
    path('lecturers/',views.lecturers, name='lecturers'),
    path('classes/',views.classes, name='classes'),
    path('rooms/edit/<int:room_id>/', views.edit_room, name='edit_room'),
    path('rooms/delete/<int:room_id>/', views.delete_room, name='delete_room'),
    path('classes/edit/<int:class_id>/', views.edit_class, name='edit_class'),
    path('classes/delete/<int:class_id>/', views.delete_class, name='delete_class'),
    path('lecturers/edit/<int:lecturer_id>/', views.edit_lecturer, name='edit_lecturer'),
    path('lecturers/delete/<int:lecturer_id>/', views.delete_lecturer, name='delete_lecturer'),
    path('courses/edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('courses/delete/<int:course_id>/', views.delete_course, name='delete_course'),
    path('view/', views.view_timetable_hub, name='view_timetable'),
    path('class_timetable/<int:class_id>/', views.class_timetable, name='class_timetable'),
    path('lecturer_timetable/<int:lecturer_id>/', views.lecturer_timetable, name='lecturer_timetable'),
    path('add_user/', views.add_user_frontend, name='add_user_frontend'),

    # Exam timetable viewing URLs
    path('exam_timetable_hub/', views.exam_timetable_hub, name='exam_timetable_hub'),
    path('college_exam_timetable/<int:college_id>/', views.college_exam_timetable, name='college_exam_timetable'),
    path('class_exam_timetable/<int:class_id>/', views.class_exam_timetable, name='class_exam_timetable'),
    path('lecturer_exam_timetable/<int:lecturer_id>/', views.lecturer_exam_timetable, name='lecturer_exam_timetable'),

    # Exam schedule and invigilation URLs
    path('exam_schedules/', views.exam_schedule_list, name='exam_schedule_list'),
    path('exam_schedule/<int:schedule_id>/', views.exam_schedule_detail, name='exam_schedule_detail'),
    path('invigilation_assignments/', views.invigilation_assignments, name='invigilation_assignments'),
    path('lecturer_invigilation/<int:lecturer_id>/', views.lecturer_invigilation_schedule, name='lecturer_invigilation_schedule'),
]
