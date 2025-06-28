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

]
