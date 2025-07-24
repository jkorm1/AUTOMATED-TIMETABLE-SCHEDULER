import csv
import random
import string
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from Timetable.models import StudentProfile, LecturerProfile, Class, Department
from django.db import transaction

class Command(BaseCommand):
    help = 'Create users (students/lecturers) from a CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        with open(options['csv_file'], newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                email = row['email']
                first_name = row['first_name']
                last_name = row['last_name']
                role = row['role'].lower()
                username = email.split('@')[0]
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name
                    )
                    if role == 'student':
                        student_id = row['student_id']
                        class_obj = Class.objects.get(id=row['class_id'])
                        StudentProfile.objects.create(
                            user=user,
                            student_id=student_id,
                            class_obj=class_obj
                        )
                        group, _ = Group.objects.get_or_create(name='Students')
                        user.groups.add(group)
                        self.stdout.write(self.style.SUCCESS(f"Student: {username} | {email} | {password}"))
                    elif role == 'lecturer':
                        lecturer_id = row['lecturer_id']
                        department = Department.objects.get(id=row['department_id'])
                        LecturerProfile.objects.create(
                            user=user,
                            lecturer_id=lecturer_id,
                            department=department
                        )
                        group, _ = Group.objects.get_or_create(name='Lecturers')
                        user.groups.add(group)
                        self.stdout.write(self.style.SUCCESS(f"Lecturer: {username} | {email} | {password}"))
                    else:
                        self.stdout.write(self.style.ERROR(f"Unknown role: {role} for {email}")) 