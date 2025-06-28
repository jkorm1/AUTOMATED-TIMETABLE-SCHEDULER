from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('generate_schedule/', views.generate_schedule, name = 'generate_schedule'),
    path('generate/',views.generate, name='generate'),
    
]
