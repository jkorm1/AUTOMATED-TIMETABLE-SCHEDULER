from django.core.management.base import BaseCommand
from Timetable.models import College, Department, Class, Course, Room, Lecturer, Building, RoomType, LabType, CourseType
from django.db import transaction
import random

class Command(BaseCommand):
    help = 'Clear and seed the database with realistic KNUST data for scheduling.'

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            # Delete all existing data
            Course.objects.all().delete()
            Lecturer.objects.all().delete()
            Class.objects.all().delete()
            Department.objects.all().delete()
            College.objects.all().delete()
            Room.objects.all().delete()
            Building.objects.all().delete()
            RoomType.objects.all().delete()
            LabType.objects.all().delete()
            CourseType.objects.all().delete()

            self.stdout.write(self.style.SUCCESS('Seeding KNUST data...'))

            # --- HARD-CODED, REALISTIC DATA FOR TESTING ---
            # Colleges
            college_data = [
                {'code': 'COS', 'name': 'College of Science', 'description': 'College of Science at KNUST'},
                {'code': 'COE', 'name': 'College of Engineering', 'description': 'College of Engineering at KNUST'},
            ]
            colleges = {}
            for c in college_data:
                colleges[c['name']], _ = College.objects.get_or_create(code=c['code'], name=c['name'], defaults={'description': c['description']})

            # Buildings
            building_data = [
                {'code': 'COSB1', 'name': 'Science Block', 'college': colleges['College of Science']},
                {'code': 'COEB1', 'name': 'Engineering Block', 'college': colleges['College of Engineering']},
            ]
            buildings = {}
            for b in building_data:
                buildings[b['name']], _ = Building.objects.get_or_create(code=b['code'], name=b['name'], college=b['college'])

            # Departments
            dept_data = [
                {'code': 'CS', 'name': 'Department of Computer Science', 'college': colleges['College of Science'], 'building': buildings['Science Block']},
                {'code': 'MATH', 'name': 'Department of Mathematics', 'college': colleges['College of Science'], 'building': buildings['Science Block']},
                {'code': 'PHY', 'name': 'Department of Physics', 'college': colleges['College of Science'], 'building': buildings['Science Block']},
                {'code': 'CENG', 'name': 'Department of Computer Engineering', 'college': colleges['College of Engineering'], 'building': buildings['Engineering Block']},
                {'code': 'CIV', 'name': 'Department of Civil Engineering', 'college': colleges['College of Engineering'], 'building': buildings['Engineering Block']},
                {'code': 'ELEC', 'name': 'Department of Electrical Engineering', 'college': colleges['College of Engineering'], 'building': buildings['Engineering Block']},
            ]
            departments = {}
            for d in dept_data:
                departments[d['name']], _ = Department.objects.get_or_create(code=d['code'], name=d['name'], college=d['college'], building=d['building'])

            # Room Types, Lab Types, Course Types
            lecture_hall, _ = RoomType.objects.get_or_create(name='Lecture Hall')
            lab_type, _ = LabType.objects.get_or_create(name='IT')
            course_type_lecture, _ = CourseType.objects.get_or_create(name='Lecture')
            course_type_lab, _ = CourseType.objects.get_or_create(name='Lab')

            # Rooms (2 floors per building, 2 rooms per floor, realistic codes)
            room_data = [
                # Science Block 1
                {'code': 'COSB1-ff1', 'building': buildings['Science Block'], 'room_type': lecture_hall, 'lab_type': lab_type, 'capacity': 120, 'name': 'Science Block 1 First Floor Room 1'},
                {'code': 'COSB1-ff2', 'building': buildings['Science Block'], 'room_type': lecture_hall, 'lab_type': lab_type, 'capacity': 80, 'name': 'Science Block 1 First Floor Room 2'},
                {'code': 'COSB1-sf1', 'building': buildings['Science Block'], 'room_type': lecture_hall, 'lab_type': lab_type, 'capacity': 100, 'name': 'Science Block 1 Second Floor Room 1'},
                {'code': 'COSB1-sf2', 'building': buildings['Science Block'], 'room_type': lecture_hall, 'lab_type': lab_type, 'capacity': 90, 'name': 'Science Block 1 Second Floor Room 2'},
                # Engineering Block 1
                {'code': 'COEB1-ff1', 'building': buildings['Engineering Block'], 'room_type': lecture_hall, 'lab_type': lab_type, 'capacity': 110, 'name': 'Engineering Block 1 First Floor Room 1'},
                {'code': 'COEB1-ff2', 'building': buildings['Engineering Block'], 'room_type': lecture_hall, 'lab_type': lab_type, 'capacity': 95, 'name': 'Engineering Block 1 First Floor Room 2'},
                {'code': 'COEB1-sf1', 'building': buildings['Engineering Block'], 'room_type': lecture_hall, 'lab_type': lab_type, 'capacity': 105, 'name': 'Engineering Block 1 Second Floor Room 1'},
                {'code': 'COEB1-sf2', 'building': buildings['Engineering Block'], 'room_type': lecture_hall, 'lab_type': lab_type, 'capacity': 100, 'name': 'Engineering Block 1 Second Floor Room 2'},
            ]
            rooms = {}
            for r in room_data:
                rooms[r['code']], _ = Room.objects.get_or_create(
                    code=r['code'], building=r['building'], room_type=r['room_type'], lab_type=r['lab_type'],
                    capacity=r['capacity'], dimensions='10x10', max_courses=1, proctors_required=1, is_overflow=False
                )

            # Classes (4 per department: 100, 200, 300, 400)
            class_data = []
            for dept in departments.values():
                for level in [100, 200, 300, 400]:
                    class_data.append({
                        'code': f'{dept.code}L{level}',
                        'name': f'{dept.name} Level {level}',
                        'department': dept,
                        'level': level,
                        'size': 80 if dept.code in ['CS', 'CENG'] else 60
                    })
            classes = {}
            for c in class_data:
                classes[(c['department'].name, c['level'])], _ = Class.objects.get_or_create(
                    code=c['code'], name=c['name'], department=c['department'], level=c['level'], size=c['size']
                )

            # Courses (5 per class/level, realistic codes/titles)
            course_data = [
                # Computer Science
                {'code': 'CS151', 'title': 'Introduction to Computer Science', 'department': departments['Department of Computer Science'], 'level': 100},
                {'code': 'CS152', 'title': 'Programming Fundamentals', 'department': departments['Department of Computer Science'], 'level': 100},
                {'code': 'CS153', 'title': 'Discrete Mathematics', 'department': departments['Department of Computer Science'], 'level': 100},
                {'code': 'CS154', 'title': 'Computer Literacy', 'department': departments['Department of Computer Science'], 'level': 100},
                {'code': 'CS155', 'title': 'Digital Logic', 'department': departments['Department of Computer Science'], 'level': 100},
                # Mathematics
                {'code': 'MATH151', 'title': 'Algebra and Trigonometry', 'department': departments['Department of Mathematics'], 'level': 100},
                {'code': 'MATH152', 'title': 'Calculus I', 'department': departments['Department of Mathematics'], 'level': 100},
                {'code': 'MATH153', 'title': 'Statistics I', 'department': departments['Department of Mathematics'], 'level': 100},
                {'code': 'MATH154', 'title': 'Mathematical Methods', 'department': departments['Department of Mathematics'], 'level': 100},
                {'code': 'MATH155', 'title': 'Linear Algebra I', 'department': departments['Department of Mathematics'], 'level': 100},
                # Physics
                {'code': 'PHY151', 'title': 'General Physics I', 'department': departments['Department of Physics'], 'level': 100},
                {'code': 'PHY152', 'title': 'General Physics II', 'department': departments['Department of Physics'], 'level': 100},
                {'code': 'PHY153', 'title': 'Mechanics', 'department': departments['Department of Physics'], 'level': 100},
                {'code': 'PHY154', 'title': 'Thermodynamics', 'department': departments['Department of Physics'], 'level': 100},
                {'code': 'PHY155', 'title': 'Waves and Optics', 'department': departments['Department of Physics'], 'level': 100},
                # Computer Engineering
                {'code': 'CENG151', 'title': 'Introduction to Computer Engineering', 'department': departments['Department of Computer Engineering'], 'level': 100},
                {'code': 'CENG152', 'title': 'Engineering Mathematics', 'department': departments['Department of Computer Engineering'], 'level': 100},
                {'code': 'CENG153', 'title': 'Programming for Engineers', 'department': departments['Department of Computer Engineering'], 'level': 100},
                {'code': 'CENG154', 'title': 'Digital Systems', 'department': departments['Department of Computer Engineering'], 'level': 100},
                {'code': 'CENG155', 'title': 'Electrical Circuits', 'department': departments['Department of Computer Engineering'], 'level': 100},
                # Civil Engineering
                {'code': 'CIV151', 'title': 'Introduction to Civil Engineering', 'department': departments['Department of Civil Engineering'], 'level': 100},
                {'code': 'CIV152', 'title': 'Engineering Drawing', 'department': departments['Department of Civil Engineering'], 'level': 100},
                {'code': 'CIV153', 'title': 'Surveying I', 'department': departments['Department of Civil Engineering'], 'level': 100},
                {'code': 'CIV154', 'title': 'Construction Materials', 'department': departments['Department of Civil Engineering'], 'level': 100},
                {'code': 'CIV155', 'title': 'Statics', 'department': departments['Department of Civil Engineering'], 'level': 100},
                # Electrical Engineering
                {'code': 'ELEC151', 'title': 'Introduction to Electrical Engineering', 'department': departments['Department of Electrical Engineering'], 'level': 100},
                {'code': 'ELEC152', 'title': 'Circuit Analysis', 'department': departments['Department of Electrical Engineering'], 'level': 100},
                {'code': 'ELEC153', 'title': 'Electromagnetics', 'department': departments['Department of Electrical Engineering'], 'level': 100},
                {'code': 'ELEC154', 'title': 'Electronics I', 'department': departments['Department of Electrical Engineering'], 'level': 100},
                {'code': 'ELEC155', 'title': 'Engineering Mathematics I', 'department': departments['Department of Electrical Engineering'], 'level': 100},
                # ... (repeat for 200, 300, 400 levels for each department)
            ]
            # For brevity, only 100-level courses are shown. You can expand this for all levels.
            courses = {}
            for c in course_data:
                course, _ = Course.objects.get_or_create(
                    code=c['code'], title=c['title'], course_type=course_type_lecture, department=c['department'],
                    credit_hours=3, enrollment=80
                )
                course_class = classes[(c['department'].name, c['level'])]
                course.classes.set([course_class])
                courses[c['code']] = course

            # Lecturers (realistic names, some teach in both colleges)
            lecturer_data = [
                {'name': 'Dr. Kwame Mensah', 'departments': ['Department of Computer Science', 'Department of Computer Engineering']},
                {'name': 'Prof. Akosua Boateng', 'departments': ['Department of Mathematics']},
                {'name': 'Dr. Kofi Asante', 'departments': ['Department of Physics', 'Department of Civil Engineering']},
                {'name': 'Dr. Ama Serwaa', 'departments': ['Department of Computer Science']},
                {'name': 'Prof. Yaw Ofori', 'departments': ['Department of Electrical Engineering']},
                {'name': 'Dr. Esi Sarpong', 'departments': ['Department of Mathematics', 'Department of Computer Engineering']},
                {'name': 'Dr. Samuel Opoku', 'departments': ['Department of Physics']},
                {'name': 'Dr. Nana Adjei', 'departments': ['Department of Civil Engineering']},
                {'name': 'Prof. Abena Owusu', 'departments': ['Department of Computer Science', 'Department of Electrical Engineering']},
                {'name': 'Dr. Michael Owusu', 'departments': ['Department of Mathematics']},
                {'name': 'Dr. Linda Agyeman', 'departments': ['Department of Physics']},
                {'name': 'Dr. Kojo Antwi', 'departments': ['Department of Computer Engineering']},
                {'name': 'Dr. Patience Osei', 'departments': ['Department of Civil Engineering']},
                {'name': 'Prof. Daniel Tetteh', 'departments': ['Department of Electrical Engineering']},
                {'name': 'Dr. Josephine Addo', 'departments': ['Department of Computer Science']},
                {'name': 'Dr. Isaac Quaye', 'departments': ['Department of Mathematics']},
                {'name': 'Dr. Emelia Appiah', 'departments': ['Department of Physics']},
                {'name': 'Dr. Felix Owusu', 'departments': ['Department of Computer Engineering']},
                {'name': 'Dr. Matilda Darko', 'departments': ['Department of Civil Engineering']},
                {'name': 'Dr. Richmond Amponsah', 'departments': ['Department of Electrical Engineering']},
            ]
            lecturers = {}
            for l in lecturer_data:
                for dept_name in l['departments']:
                    dept = departments[dept_name]
                    lecturer, _ = Lecturer.objects.get_or_create(
                        name=l['name'], department=dept, is_active=True, max_courses=4
                    )
                    lecturers[(l['name'], dept_name)] = lecturer

            # Assign lecturers to courses (2 per course, prefer department lecturers, allow cross-college)
            for c in course_data:
                dept_lects = [lecturers[(l['name'], c['department'].name)] for l in lecturer_data if c['department'].name in l['departments']]
                # Add cross-college lecturer if available
                possible_lects = dept_lects + [lecturers[(l['name'], d)] for l in lecturer_data for d in l['departments'] if d != c['department'].name][:2]
                course = courses[c['code']]
                course.lecturers.set(possible_lects[:2])

            self.stdout.write(self.style.SUCCESS('Database seeded with realistic, hard-coded KNUST-style data!')) 