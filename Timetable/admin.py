from django.contrib import admin
from .models import Room,Class,Lecturer,Course

# Register your models here.
admin.site.register(Room)
admin.site.register(Class)
admin.site.register(Lecturer)
admin.site.register(Course)