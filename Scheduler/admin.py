from django.contrib import admin
from .models import (
    ExamSchedule,
    ExamRoomAssignment,
    ExamRoomClassAllocation,
    StudentExamAllocation
)


@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ('course', 'date', 'time_slot', 'created_at')
    list_filter = ('date', 'time_slot')
    search_fields = ('course__code',)


@admin.register(ExamRoomAssignment)
class ExamRoomAssignmentAdmin(admin.ModelAdmin):
    list_display = ('exam', 'room', 'seating_manual')
    filter_horizontal = ('proctors',)
    search_fields = ('exam__course__code', 'room__name')


@admin.register(ExamRoomClassAllocation)
class ExamRoomClassAllocationAdmin(admin.ModelAdmin):
    list_display = ('room_assignment', 'class_assigned', 'student_count')
    search_fields = ('class_assigned__code', 'room_assignment__room__name')


@admin.register(StudentExamAllocation)
class StudentExamAllocationAdmin(admin.ModelAdmin):
    list_display = ('student_index', 'exam', 'room', 'column_number')
    list_filter = ('exam', 'room')
    search_fields = ('student_index', 'exam__course__code', 'room__name')
