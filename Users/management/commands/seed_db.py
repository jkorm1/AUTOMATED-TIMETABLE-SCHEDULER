from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from Users.models import StudentProfile, LecturerProfile

class Command(BaseCommand):
    help = 'Seed the database with initial test data.'

    def handle(self, *args, **options):
        User = get_user_model()
        # Student user
        email = 'jkorm@example.com'
        username = 'Jkorm'
        password = 'jkorm12345'
        index_number = '123456'
        program = 'Computer Science'
        level = '100'

        if not User.objects.filter(email=email).exists():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_student=True
            )
            StudentProfile.objects.create(
                user=user,
                index_number=index_number,
                program=program,
                level=level
            )
            self.stdout.write(self.style.SUCCESS(f'Created student user: {email} / {index_number}'))
        else:
            self.stdout.write(self.style.WARNING(f'User {email} already exists.'))

        # Lecturer user
        lec_email = 'lecturer@example.com'
        lec_username = 'Lecturer1'
        lec_password = 'lecturer12345'
        staff_id = 'L123'
        department = 'Mathematics'

        if not User.objects.filter(email=lec_email).exists():
            lec_user = User.objects.create_user(
                username=lec_username,
                email=lec_email,
                password=lec_password,
                is_lecturer=True
            )
            LecturerProfile.objects.create(
                user=lec_user,
                staff_id=staff_id,
                department=department
            )
            self.stdout.write(self.style.SUCCESS(f'Created lecturer user: {lec_email} / {staff_id}'))
        else:
            self.stdout.write(self.style.WARNING(f'User {lec_email} already exists.')) 