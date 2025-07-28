#!/usr/bin/env python
"""
Quick setup script for exam timetable data
Run this with: python manage.py shell < setup_exam_data.py
"""

from Timetable.models import Lecturer

print("Setting up exam timetable data...")

# Mark some lecturers as proctors (first 10 active lecturers)
lecturers = Lecturer.objects.filter(is_active=True)[:10]
marked_count = 0

for lecturer in lecturers:
    if not lecturer.is_proctor:
        lecturer.is_proctor = True
        lecturer.save()
        marked_count += 1
        print(f"✓ Marked {lecturer.name} as proctor")

if marked_count == 0:
    print("All lecturers are already marked as proctors!")
else:
    print(f"\n✅ Successfully marked {marked_count} lecturers as proctors")

print("\n📋 What you need to do next:")
print("1. Go to http://127.0.0.1:8000/admin/")
print("2. Navigate to Timetable → Lecturers")
print("3. Mark more lecturers as proctors if needed (check 'Is proctor')")
print("4. Ensure rooms have sufficient capacity for your classes")
print("5. Go to http://127.0.0.1:8000/scheduler/generate_exam_schedule/")
print("6. Select a college and optionally set an exam start date")
print("7. Click 'Generate Exam Schedule'")

print("\n🎯 The system will automatically:")
print("- Generate 3 weeks of exam dates (Monday-Friday only)")
print("- Create time slots (9:00-11:00, 14:00-16:00, 18:00-20:00)")
print("- Distribute courses across the 3 weeks")
print("- Assign invigilators to each exam")
print("- Ensure no conflicts between classes, rooms, or invigilators") 
 
 