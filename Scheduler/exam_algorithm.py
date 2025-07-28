import random
from collections import defaultdict
from datetime import date, timedelta, time

def generate_exam_dates_and_slots(start_date, exam_duration_hours=2):
    """Automatically generate exam dates for 3 working weeks and time slots"""
    exam_dates = []
    exam_time_slots = []
    
    # Generate 3 weeks of working days (Monday-Friday)
    current_date = start_date
    week_count = 0
    
    while week_count < 3:
        # Skip weekends
        while current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            current_date += timedelta(days=1)
        
        if current_date.weekday() < 5:  # Monday-Friday
            exam_dates.append(current_date)
        
        current_date += timedelta(days=1)
        
        # Check if we've completed a week
        if len(exam_dates) % 5 == 0 and len(exam_dates) > 0:
            week_count += 1
    
    # Generate time slots for each day
    # More slots within 8am-7pm range to accommodate more exams
    time_ranges = [
        (time(8, 0), time(10, 0)),   # 8:00-10:00
        (time(10, 30), time(12, 30)), # 10:30-12:30
        (time(13, 0), time(15, 0)),   # 13:00-15:00
        (time(15, 30), time(17, 30)), # 15:30-17:30
        (time(18, 0), time(20, 0))    # 18:00-20:00 (if needed)
    ]
    
    for exam_date in exam_dates:
        for i, (start_time, end_time) in enumerate(time_ranges):
            slot_code = f"EXAM_{exam_date.strftime('%Y%m%d')}_{i+1}"
            exam_time_slots.append({
                'date': exam_date,
                'start_time': start_time,
                'end_time': end_time,
                'code': slot_code,
                'day_name': exam_date.strftime('%A')
            })
    
    return exam_dates, exam_time_slots

def distribute_courses_across_weeks(courses_data, exam_dates, exam_time_slots):
    """Distribute courses across 3 weeks based on class and course count"""
    print(f"Distributing {len(courses_data)} courses across {len(exam_dates)} dates")
    
    # Group courses by class
    class_courses = defaultdict(list)
    for course_data in courses_data:
        course = course_data['course']
        classes = course_data['classes']
        for class_obj in classes:
            class_courses[class_obj].append(course)
    
    print(f"Found {len(class_courses)} classes with courses")
    
    # Debug: Print the distribution
    for class_obj, courses_list in class_courses.items():
        print(f"  {class_obj.code}: {len(courses_list)} courses")
        for course in courses_list:
            print(f"    - {course.code}")
    
    # Calculate total exam sessions needed
    total_sessions = sum(len(courses) for courses in class_courses.values())
    
    # Distribute across 3 weeks (15 working days, 5 slots per day = 75 total slots)
    total_available_slots = len(exam_dates) * 5  # 5 time slots per day
    
    if total_sessions > total_available_slots:
        print(f"Warning: Need {total_sessions} exam sessions but only {total_available_slots} slots available")
        print(f"Available: {len(exam_dates)} days × 5 slots = {total_available_slots} slots")
        print(f"Required: {total_sessions} sessions")
        print(f"Shortage: {total_sessions - total_available_slots} sessions")
        return []
    
    # Create exam schedule entries
    exam_schedule = []
    slot_index = 0
    
    for class_obj, courses in class_courses.items():
        print(f"Distributing {len(courses)} courses for {class_obj.code}")
        
        for course in courses:
            if slot_index >= len(exam_time_slots):
                print(f"Warning: No more slots available for {course.code}")
                break
                
            slot = exam_time_slots[slot_index]
            
            # Find suitable room
            room = find_suitable_room_for_class(class_obj)
            if not room:
                print(f"Warning: No suitable room found for {class_obj.code}")
                slot_index += 1
                continue
            
            exam_entry = {
                'course': course,
                'class': class_obj,
                'date': slot['date'],
                'time_slot': slot,
                'room': room,
                'duration': 120,  # 2 hours
                'week': (slot_index // 25) + 1,  # Which week (1, 2, or 3) - 5 slots per day * 5 days = 25 slots per week
                'invigilators': [],
                'required_invigilators': calculate_required_invigilators(class_obj, room)
            }
            
            exam_schedule.append(exam_entry)
            slot_index += 1
    
    return exam_schedule

def find_suitable_room_for_class(class_obj):
    """Find a room that can accommodate the class"""
    from Timetable.models import Room
    
    suitable_rooms = Room.objects.filter(
        capacity__gte=class_obj.size,
        is_overflow=False
    ).order_by('capacity')
    
    if suitable_rooms.exists():
        return suitable_rooms.first()
    return None

def assign_invigilators_to_schedule(exam_schedule, invigilators):
    """Assign invigilators to exam sessions"""
    from collections import defaultdict
    
    # Track invigilator assignments to avoid conflicts
    invigilator_assignments = defaultdict(set)  # invigilator -> set of (date, time_slot)
    
    for entry in exam_schedule:
        required_count = entry['required_invigilators']
        available_invigilators = []
        
        # Find available invigilators for this time slot
        for invigilator in invigilators:
            if not invigilator.is_proctor or not invigilator.is_active:
                continue
                
            # Check if invigilator is already assigned to this date/time
            slot_key = (entry['date'], entry['time_slot']['code'])
            if slot_key not in invigilator_assignments[invigilator]:
                available_invigilators.append(invigilator)
        
        if len(available_invigilators) >= required_count:
            selected_invigilators = random.sample(available_invigilators, required_count)
            entry['invigilators'] = selected_invigilators
            
            # Update invigilator assignments
            for invigilator in selected_invigilators:
                slot_key = (entry['date'], entry['time_slot']['code'])
                invigilator_assignments[invigilator].add(slot_key)
        else:
            print(f"Warning: Not enough invigilators for {entry['course'].code} - {entry['class'].code}")
            entry['invigilators'] = available_invigilators[:required_count]

def run_exam_genetic_algorithm(
    exam_courses,
    start_date,
    invigilators,
    exam_duration_hours=2,
    generations=50,
    population_size=30
):
    """Main genetic algorithm for exam scheduling with automatic date/time generation"""
    
    print(f"Starting exam scheduling for 3 weeks from {start_date}")
    print(f"Number of exam courses: {len(exam_courses)}")
    print(f"Number of invigilators: {len(invigilators)}")
    
    # Step 1: Generate exam dates and time slots automatically
    exam_dates, exam_time_slots = generate_exam_dates_and_slots(start_date, exam_duration_hours)
    print(f"Generated {len(exam_dates)} exam dates and {len(exam_time_slots)} time slots")
    
    # Step 2: Distribute courses across weeks
    exam_schedule = distribute_courses_across_weeks(exam_courses, exam_dates, exam_time_slots)
    print(f"Distributed {len(exam_schedule)} exam sessions")
    
    # Step 3: Assign invigilators
    assign_invigilators_to_schedule(exam_schedule, invigilators)
    
    # Step 4: Optimize using genetic algorithm
    if exam_schedule:
        optimized_schedule = optimize_exam_schedule_genetic(
            exam_schedule, exam_dates, exam_time_slots, invigilators,
            generations, population_size
        )
        return optimized_schedule
    else:
        print("No exam schedule could be created")
        return []

def optimize_exam_schedule_genetic(exam_schedule, exam_dates, exam_time_slots, invigilators, generations, population_size):
    """Optimize the exam schedule using genetic algorithm"""
    
    # Create initial population
    population = []
    for _ in range(population_size):
        # Create a variant of the schedule by swapping some time slots
        variant = exam_schedule.copy()
        for entry in variant:
            if random.random() < 0.1:  # 10% chance to swap time slot
                new_slot = random.choice(exam_time_slots)
                entry['time_slot'] = new_slot
                entry['date'] = new_slot['date']
        population.append(variant)
    
    # Genetic algorithm optimization
    for gen in range(generations):
        # Calculate fitness for each schedule
        fitness_scores = [calculate_exam_fitness(schedule) for schedule in population]
        
        # Select best schedules
        sorted_population = [x for _, x in sorted(zip(fitness_scores, population), key=lambda pair: pair[0], reverse=True)]
        
        # Keep top 20% unchanged
        elites = sorted_population[:population_size // 5]
        
        # Create new population through crossover and mutation
        new_population = elites.copy()
        
        while len(new_population) < population_size:
            # Crossover
            parent1, parent2 = random.sample(sorted_population[:10], 2)
            child = crossover_exam_schedules(parent1, parent2)
            
            # Mutation
            if random.random() < 0.1:
                child = mutate_exam_schedule(child, exam_time_slots)
            
            new_population.append(child)
        
        population = new_population
        
        if gen % 10 == 0:
            best_score = max(fitness_scores)
            print(f"Generation {gen}: Best fitness = {best_score}")
    
    # Return best schedule
    final_fitness_scores = [calculate_exam_fitness(schedule) for schedule in population]
    best_index = final_fitness_scores.index(max(final_fitness_scores))
    return population[best_index]

def calculate_exam_fitness(schedule):
    """Calculate fitness score for exam schedule"""
    score = 1000
    
    # Check for conflicts
    slot_usage = defaultdict(set)  # (date, time_slot) -> set of classes
    room_usage = defaultdict(set)  # (date, time_slot) -> set of rooms
    
    for entry in schedule:
        slot_key = (entry['date'], entry['time_slot']['code'])
        
        # Check class conflicts
        if entry['class'] in slot_usage[slot_key]:
            score -= 100  # Hard constraint violation
        else:
            slot_usage[slot_key].add(entry['class'])
        
        # Check room conflicts
        if entry['room'] in room_usage[slot_key]:
            score -= 100  # Hard constraint violation
        else:
            room_usage[slot_key].add(entry['room'])
        
        # Bonus for good distribution across weeks
        if entry['week'] in [1, 2, 3]:  # Properly distributed
            score += 10
        
        # Penalty for insufficient invigilators
        if len(entry['invigilators']) < entry['required_invigilators']:
            score -= 30 * (entry['required_invigilators'] - len(entry['invigilators']))
    
    return score

def crossover_exam_schedules(parent1, parent2):
    """Crossover two exam schedules"""
    if len(parent1) < 2 or len(parent2) < 2:
        return parent1.copy()
    
    crossover_point = random.randint(1, min(len(parent1), len(parent2)) - 1)
    child = parent1[:crossover_point] + parent2[crossover_point:]
    
    # Remove duplicates
    seen = set()
    unique_child = []
    for entry in child:
        key = (entry['course'].id, entry['class'].id)
        if key not in seen:
            seen.add(key)
            unique_child.append(entry)
    
    return unique_child

def mutate_exam_schedule(schedule, exam_time_slots):
    """Mutate exam schedule"""
    mutated = schedule.copy()
    
    for entry in mutated:
        if random.random() < 0.1:  # 10% mutation rate
            new_slot = random.choice(exam_time_slots)
            entry['time_slot'] = new_slot
            entry['date'] = new_slot['date']
            entry['week'] = (exam_time_slots.index(new_slot) // 15) + 1
    
    return mutated

def calculate_required_invigilators(class_obj, room):
    """Calculate required number of invigilators"""
    student_count = class_obj.size
    
    if student_count <= 50:
        return max(2, room.proctors_required)
    elif student_count <= 100:
        return max(3, room.proctors_required)
    else:
        return max(4, room.proctors_required) 
 
 