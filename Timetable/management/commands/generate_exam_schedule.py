from django.core.management.base import BaseCommand
from django.db import transaction
from Timetable.models import (
    ExamDate, TimeSlot, Course, Class, Room, Lecturer, 
    ExamSchedule, InvigilationAssignment, ProctorAssignment
)
from collections import defaultdict
import random


class Command(BaseCommand):
    help = 'Generate exam schedule and assign invigilators'

    def add_arguments(self, parser):
        parser.add_argument(
            '--exam-date',
            type=str,
            help='Exam date (YYYY-MM-DD)',
        )
        parser.add_argument(
            '--college',
            type=str,
            help='College code to generate schedule for',
        )
        parser.add_argument(
            '--auto-assign-invigilators',
            action='store_true',
            help='Automatically assign invigilators to exams',
        )

    def handle(self, *args, **options):
        exam_date_str = options['exam_date']
        college_code = options['college']
        auto_assign = options['auto_assign_invigilators']

        try:
            # Get exam date
            if exam_date_str:
                exam_date = ExamDate.objects.get(date=exam_date_str)
            else:
                exam_date = ExamDate.objects.first()
                if not exam_date:
                    self.stdout.write(
                        self.style.ERROR('No exam dates found. Please create exam dates first.')
                    )
                    return

            # Get available time slots for exams
            exam_time_slots = TimeSlot.objects.filter(is_exam_slot=True)
            if not exam_time_slots.exists():
                self.stdout.write(
                    self.style.ERROR('No exam time slots found. Please create time slots with is_exam_slot=True.')
                )
                return

            # Get courses and classes
            if college_code:
                courses = Course.objects.filter(department__college__code=college_code)
                classes = Class.objects.filter(department__college__code=college_code)
            else:
                courses = Course.objects.all()
                classes = Class.objects.all()

            # Get available rooms
            rooms = Room.objects.filter(is_overflow=False).order_by('capacity')

            # Get available invigilators
            invigilators = Lecturer.objects.filter(is_proctor=True, is_active=True)

            if not invigilators.exists():
                self.stdout.write(
                    self.style.ERROR('No invigilators found. Please mark lecturers as proctors first.')
                )
                return

            self.stdout.write(f'Generating exam schedule for {exam_date.date}')
            self.stdout.write(f'Found {courses.count()} courses, {classes.count()} classes, {rooms.count()} rooms, {invigilators.count()} invigilators')

            # Generate exam schedule
            schedules_created = self.generate_exam_schedules(
                exam_date, exam_time_slots, courses, classes, rooms
            )

            if auto_assign and schedules_created:
                self.assign_invigilators(exam_date, invigilators)

            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {schedules_created} exam schedules')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )

    def generate_exam_schedules(self, exam_date, time_slots, courses, classes, rooms):
        """Generate exam schedules for courses and classes"""
        schedules_created = 0
        
        with transaction.atomic():
            # Clear existing schedules for this date
            ExamSchedule.objects.filter(exam_date=exam_date).delete()
            
            # Group classes by department for better scheduling
            classes_by_dept = defaultdict(list)
            for class_obj in classes:
                classes_by_dept[class_obj.department].append(class_obj)
            
            # Schedule exams for each department
            for dept, dept_classes in classes_by_dept.items():
                dept_courses = courses.filter(department=dept)
                
                for course in dept_courses:
                    # Find classes that take this course
                    course_classes = [c for c in dept_classes if course in c.courses.all()]
                    
                    for class_obj in course_classes:
                        # Find suitable room
                        room = self.find_suitable_room(class_obj, rooms)
                        if not room:
                            self.stdout.write(
                                self.style.WARNING(f'No suitable room found for {class_obj.code} ({class_obj.size} students)')
                            )
                            continue
                        
                        # Find available time slot
                        time_slot = self.find_available_time_slot(exam_date, class_obj, time_slots)
                        if not time_slot:
                            self.stdout.write(
                                self.style.WARNING(f'No available time slot for {class_obj.code}')
                            )
                            continue
                        
                        # Create exam schedule
                        schedule = ExamSchedule.objects.create(
                            exam_date=exam_date,
                            time_slot=time_slot,
                            course=course,
                            program_class=class_obj,
                            room=room,
                            exam_duration=120,  # 2 hours default
                            is_scheduled=True
                        )
                        schedules_created += 1
                        
                        self.stdout.write(
                            f'Created: {course.code} - {class_obj.code} in {room.code} at {time_slot}'
                        )
        
        return schedules_created

    def find_suitable_room(self, class_obj, rooms):
        """Find a room that can accommodate the class"""
        class_size = class_obj.size
        
        # Try to find a room with capacity close to class size
        suitable_rooms = rooms.filter(capacity__gte=class_size).order_by('capacity')
        
        if suitable_rooms.exists():
            return suitable_rooms.first()
        
        return None

    def find_available_time_slot(self, exam_date, class_obj, time_slots):
        """Find an available time slot for the class"""
        # Check existing schedules for this date and class
        existing_schedules = ExamSchedule.objects.filter(
            exam_date=exam_date,
            program_class=class_obj
        )
        
        used_time_slots = set(existing_schedules.values_list('time_slot_id', flat=True))
        available_slots = time_slots.exclude(id__in=used_time_slots)
        
        if available_slots.exists():
            return available_slots.first()
        
        return None

    def assign_invigilators(self, exam_date, invigilators):
        """Assign invigilators to exam schedules"""
        schedules = ExamSchedule.objects.filter(exam_date=exam_date, is_scheduled=True)
        
        for schedule in schedules:
            required_count = schedule.required_invigilators
            available_invigilators = list(invigilators)
            
            # Remove invigilators already assigned to overlapping time slots
            overlapping_schedules = ExamSchedule.objects.filter(
                exam_date=exam_date,
                time_slot=schedule.time_slot,
                is_scheduled=True
            ).exclude(id=schedule.id)
            
            busy_invigilators = set()
            for overlap_schedule in overlapping_schedules:
                busy_invigilators.update(overlap_schedule.invigilators.all())
            
            available_invigilators = [inv for inv in available_invigilators if inv not in busy_invigilators]
            
            if len(available_invigilators) < required_count:
                self.stdout.write(
                    self.style.WARNING(f'Not enough invigilators for {schedule}. Need {required_count}, have {len(available_invigilators)}')
                )
                continue
            
            # Assign invigilators
            selected_invigilators = random.sample(available_invigilators, required_count)
            
            for i, invigilator in enumerate(selected_invigilators):
                role = 'CHIEF' if i == 0 else 'ASSISTANT'
                
                InvigilationAssignment.objects.create(
                    exam_schedule=schedule,
                    invigilator=invigilator,
                    role=role,
                    is_confirmed=False
                )
                
                # Add to many-to-many relationship
                schedule.invigilators.add(invigilator)
            
            self.stdout.write(
                f'Assigned {len(selected_invigilators)} invigilators to {schedule}'
            ) 
 
 