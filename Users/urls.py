from django.urls import path
from . import views


urlpatterns = [
    path('', views.login_view, name='login'),                      
    path('logout/', views.logout_view, name='logout'),            
    path('redirect/', views.redirect_by_role, name='redirect_by_role'),  
    path('register/', views.register_view, name='register'),       
]
