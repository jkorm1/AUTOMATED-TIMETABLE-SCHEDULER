from django.contrib import admin
from .models import (
    Building, RoomType, LabType, Room, Department, Class, Lecturer,College,
    CourseType, Course, TimeSlot, ExamDate, ProctorAssignment, LectureSchedule,
    StudentProfile, LecturerProfile
)


admin.site.register(Building)
admin.site.register(RoomType)
admin.site.register(LabType)
admin.site.register(CourseType)
admin.site.register(ExamDate)
admin.site.register(College)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('code', 'building', 'room_type', 'capacity', 'is_overflow')
    list_filter = ('building', 'room_type', 'is_overflow')
    search_fields = ('code',)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'building')
    search_fields = ('code', 'name')


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('code', 'department', 'level', 'size')
    list_filter = ('department', 'level')
    search_fields = ('code',)


@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'staff_id', 'is_proctor', 'is_active', 'max_courses')
    list_filter = ('department', 'is_proctor', 'is_active')
    search_fields = ('name', 'staff_id')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'department', 'course_type', 'credit_hours', 'enrollment', 'requires_lab')
    list_filter = ('department', 'course_type', 'requires_lab')
    search_fields = ('code', 'title')
    filter_horizontal = ('lecturers', 'classes')


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('code', 'start_time', 'end_time', 'is_lecture_slot', 'is_exam_slot')
    list_filter = ('is_lecture_slot', 'is_exam_slot')
    search_fields = ('code',)


@admin.register(ProctorAssignment)
class ProctorAssignmentAdmin(admin.ModelAdmin):
    list_display = ('proctor', 'exam_date', 'is_available')
    list_filter = ('exam_date', 'is_available')
    search_fields = ('proctor__name',)


@admin.register(LectureSchedule)
class LectureScheduleAdmin(admin.ModelAdmin):
    list_display = ('program_class', 'course', 'lecturer', 'room', 'day', 'period')
    list_filter = ('day', 'period', 'room', 'lecturer', 'program_class')
    search_fields = ('course__code', 'program_class__code', 'lecturer__name')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'class_obj', 'first_login')
    search_fields = ('user__username', 'student_id')
    list_filter = ('class_obj', 'first_login')