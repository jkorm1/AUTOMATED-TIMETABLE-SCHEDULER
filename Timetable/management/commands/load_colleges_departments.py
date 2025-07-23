from django.core.management.base import BaseCommand
from Timetable.models import College, Department


class Command(BaseCommand):
    help = 'Load predefined colleges and their departments into the database.'

    def handle(self, *args, **kwargs):
        college_department_map = {
            'College of Science': [
                'Department of Biochemistry',
                'Department of Industrial Chemistry',
                'Department of Computer Science',
                'Department of Environmental Science',
                'Department of Food Science and Technology',
                'Department of Mathematics and Statistics',
                'Department of Physics',
            ],
            'College of Engineering': [
                'Department of Chemical Engineering',
                'Department of Civil Engineering',
                'Department of Computer Engineering',
                'Department of Electrical and Electronic Engineering',
                'Department of Geomatic Engineering',
                'Department of Mechanical Engineering',
                'Department of Petroleum Engineering',
            ],
            'College of Agriculture and Natural Resources': [
                'Department of Agricultural Economics',
                'Department of Animal Science',
                'Department of Crop and Soil Science',
                'Department of Horticulture',
                'Department of Natural Resources',
            ],
            'College of Humanities and Social Sciences': [
                'Department of Economics',
                'Department of English',
                'Department of Geography and Rural Development',
                'Department of History and Political Studies',
                'Department of Sociology and Social Work',
            ],
            'College of Art and Built Environment': [
                'Department of Architecture',
                'Department of Building Technology',
                'Department of Communication Design',
                'Department of Construction Technology and Management',
                'Department of Industrial Art',
                'Department of Painting and Sculpture',
            ],
        }

        for college_name, departments in college_department_map.items():
            # Generate base college code
            base_code = ''.join(word[0] for word in college_name.split()[:3]).upper()[:6]
            code = base_code
            suffix = 1

            # Ensure college code uniqueness
            while College.objects.filter(code=code).exists():
                code = f"{base_code}{suffix}"
                suffix += 1

            college, created = College.objects.get_or_create(
                name=college_name,
                defaults={'code': code}
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"✔ Created College: {college_name} (Code: {code})"))
            else:
                self.stdout.write(self.style.WARNING(f"✔ College already exists: {college_name}"))

            for dept_name in departments:
                # Generate base department code
                base_code = ''.join(word[0] for word in dept_name.split()[:3]).upper()[:6]
                code = base_code
                suffix = 1

                while Department.objects.filter(code=code).exists():
                    code = f"{base_code}{suffix}"
                    suffix += 1

                dept, created = Department.objects.get_or_create(
                    name=dept_name,
                    college=college,
                    defaults={'code': code}
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"  └─ Created Department: {dept_name} (Code: {code})"))
                else:
                    self.stdout.write(f"  └─ Department already exists: {dept_name}")
