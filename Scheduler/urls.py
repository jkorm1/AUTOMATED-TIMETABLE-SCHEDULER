from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [

    path('generate/',views.generate, name='generate'),
    path('college_timetable/<int:college_id>/', views.college_timetable, name='college_timetable'),
]
