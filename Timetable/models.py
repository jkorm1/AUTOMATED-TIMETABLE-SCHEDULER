from django.db import models

class Room(models.Model):
    department_building = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    room_code = models.CharField(max_length=20, unique=True)
    room_type = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.room_code} - {self.room_type}"


class Class(models.Model):
    class_code = models.CharField(max_length=20, unique=True)
    level = models.PositiveIntegerField()
    department = models.CharField(max_length=50)
    college = models.CharField(max_length=50)
    class_size = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.class_code} - {self.class_size}"


class Lecturer(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    availability = models.JSONField(blank=True, null=True)
    office_location = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    max_courses = models.PositiveIntegerField(default=4)

    def __str__(self):
        return self.name


class Course(models.Model):
    course_code = models.CharField(max_length=10, unique=True)
    course_title = models.CharField(max_length=100)
    credit_hours = models.PositiveSmallIntegerField()
    department = models.CharField(max_length=100)
    students_enrolled = models.PositiveIntegerField()
    course_prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False)
    lecturers = models.ManyToManyField(Lecturer, related_name='courses')
    classes = models.ManyToManyField(Class, related_name='courses')

    def __str__(self):
        return f"{self.course_code} - {self.course_title}"
