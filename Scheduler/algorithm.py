import random

min_periods = 2
max_periods = 5

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
lecture_hours = [
        '8:00 - 8:55', '9:00 - 9:55', '10:30 - 11:25', '11:30 - 12:25',
        '13:00 - 13:55', '14:00 - 14:55', '15:00 - 15:55',
        '16:00 - 16:55', '17:00 - 17:55', '18:00 - 18:55'
    ]


def generate_population(courses,course_credit_hours,lecturers_courses_mapping,lecturer_availability,rooms,size=20):
    population = [] 
    for _ in range(size):
        timetable = []
        used_slots = set()

        for course in courses:
            credit = course_credit_hours[course]
            lecturer = random.choice(lecturers_courses_mapping[course])
            lecturer_days = lecturer_availability.get(lecturer)
            if not lecturer_days:
                lecturer_days = {d: lecture_hours for d in days}  # fallback
            
            days_available = list(lecturer_days.keys())

            # Break credit hours into 2-period blocks and possibly 1-period block
            blocks_needed = [2] * (credit // 2)
            if credit % 2:
                blocks_needed.append(1)

            course_schedule = []

            for block_size in blocks_needed:
                scheduled = False
                attempts = 0

                while not scheduled and attempts < 100:
                    attempts += 1
                    day = random.choice(days_available)
                    room = random.choice(rooms)

                    possible_blocks = []
                    for i in range(len(lecture_hours) - block_size + 1):
                        block = lecture_hours[i:i + block_size]
                        if all((day, period, room) not in used_slots for period in block):
                            possible_blocks.append(block)

                    if possible_blocks:
                        selected_block = random.choice(possible_blocks)
                        for period in selected_block:
                            used_slots.add((day, period, room))
                            course_schedule.append({
                                'course': course,
                                'day': day,
                                'period': period,
                                'room': room,
                                'lecturer': lecturer
                            })
                        scheduled = True

                if not scheduled:
                    print(f" Could not schedule block of {block_size} for {course}")
                    break

            timetable.extend(course_schedule)
        population.append(timetable)

    return population






def fitness(schedule, student_enrollment, room_size, course_prerequisites, min_periods=2, max_periods=5):
    score = 1000
    room_occupancy = {}
    lecturer_schedule = {}
    course_periods = {}
    course_schedule = {}  

    day_order = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4}
    
    for entry in schedule:
        course = entry['course']
        day = entry['day']
        period = entry['period']
        room = entry['room']
        lecturer = entry['lecturer']

        # Constraint 1: No room conflicts (No two courses in the same room at the same time)
        room_key = (day, period, room)
        if room_key in room_occupancy:
            score -= 50  #  (Hard constraint)
        else:
            room_occupancy[room_key] = course

        # Constraint 2: No lecturer conflicts (A lecturer shouldn't be scheduled for multiple courses in the same period)
        lecturer_key = (day, period, lecturer)
        if lecturer_key in lecturer_schedule:
            score -= 50  # (Hard constraint)
        else:
            lecturer_schedule[lecturer_key] = course

        # Constraint 3: Room capacity should be sufficient for enrolled students
        if student_enrollment.get(course, 0) > room_size.get(room, 0):
            score -= 20  # (Soft constraint)

        # Track course periods and scheduling times
        course_periods[course] = course_periods.get(course, 0) + 1
        course_schedule[course] = (day, period)

    # Constraint 4: Ensure courses meet their required weekly periods
    for course, periods in course_periods.items():
        if periods < min_periods:
            score -= 20 * (min_periods - periods)  #  (Soft constraint)
        elif periods > max_periods:
            score -= 20 * (periods - max_periods)  # (Soft constraint)

    # Constraint 5: Prerequisite enforcement (Courses should not be scheduled before their prerequisites)
    for course, prereqs in course_prerequisites.items():
        if course in course_schedule:
            course_day, course_period = course_schedule[course]
            for prereq in prereqs:
                if prereq not in course_schedule:
                    score -= 20  #  (Soft constraint)
                else:
                    prereq_day, prereq_period = course_schedule[prereq]
                    if (day_order[prereq_day], prereq_period) >= (day_order[course_day], course_period):
                        score -= 20  #  (Soft constraint)

    return score


def select_parents(population, fitness_scores, num_parents):

    selected_parents = []
    
    for _ in range(num_parents):
        tournament = random.sample(list(zip(population, fitness_scores)), 3)
        best_individual = max(tournament, key=lambda x: x[1])[0]
        selected_parents.append(best_individual)

    return selected_parents

def crossover(parents, num_offsprings):
    offspring = []
    while len(offspring) < num_offsprings:
        parent1, parent2 = random.sample(parents, 2)
        cut = random.randint(1, len(parent1) - 1)
        child = parent1[:cut] + parent2[cut:]
        offspring.append(child)
    return offspring


def mutate(timetable,lecturer_availability,rooms,room_size,student_enrollment, mutation_rate=0.05,):
    mutated = [entry.copy() for entry in timetable]
    
    used_slots = set((e['day'], e['period'], e['room']) for e in timetable)

    for entry in mutated:
        course = entry['course']
        lecturer = entry['lecturer']

        if random.random() < mutation_rate:
            # Get lecturer availability if possible
            if lecturer in lecturer_availability:
                available_days = list(lecturer_availability[lecturer].keys())
                if not available_days:
                    continue
                new_day = random.choice(available_days)
                if not lecturer_availability[lecturer][new_day]:
                    continue
                new_period = random.choice(lecturer_availability[lecturer][new_day])
            else:
                new_day = random.choice(days)
                new_period = random.choice(lecture_hours)

            # Filter rooms that can hold the course and are not used at that time
            possible_rooms = [
                room for room in rooms
                if room_size[room] >= student_enrollment[course] and
                   (new_day, new_period, room) not in used_slots
            ]
            if not possible_rooms:
                continue  # skip if no valid room is found

            new_room = random.choice(possible_rooms)
            new_slot = (new_day, new_period, new_room)

            # Update if no conflict
            if new_slot not in used_slots:
                used_slots.discard((entry['day'], entry['period'], entry['room']))  # remove old slot
                used_slots.add(new_slot)

                entry['day'] = new_day
                entry['period'] = new_period
                entry['room'] = new_room

    return mutated


def run_genetic_algorithm(
    class_size ,
    rooms,
    room_size,
    days,
    lecture_hours,
    courses,
    course_credit_hours,
    student_enrollment,
    course_prerequisites,
    lecturers,
    lecturers_courses_mapping,
    lecturer_availability,
    generations=500,
    population_size=500,
    num_parents=6,
    num_offsprings=14,
    n_elites=2,
    mutation_rate=0.05
):
    population = generate_population(
    courses,  
    course_credit_hours,
    lecturers_courses_mapping,
    lecturer_availability,
    rooms,
    size=population_size
)



    for gen in range(generations):
        fitness_scores = [
            fitness(individual, student_enrollment, room_size, course_prerequisites)
            for individual in population
        ]

        # Sort population by fitness (descending)
        sorted_population = [x for _, x in sorted(zip(fitness_scores, population), key=lambda pair: pair[0], reverse=True)]
        sorted_scores = sorted(fitness_scores, reverse=True)

        # Keep top n_elites unchanged
        elites = sorted_population[:n_elites]

    
        parents = select_parents(sorted_population, sorted_scores, num_parents)


        offspring = crossover(parents, num_offsprings)

        mutated_offspring = [
        mutate(child, lecturer_availability, rooms, room_size, student_enrollment, mutation_rate)
        for child in offspring
]


        # New population: elites + mutated offspring
        population = elites + mutated_offspring

        best_score = sorted_scores[0]
        avg_score = sum(fitness_scores) / len(fitness_scores)
        print(f"Generation {gen+1}: Best Score = {best_score}, Avg Score = {avg_score:.2f}")

    final_fitness_scores = [
        fitness(individual, student_enrollment, room_size, course_prerequisites)
        for individual in population
    ]
    best_index = final_fitness_scores.index(max(final_fitness_scores))
    best_schedule = population[best_index]
    return best_schedule
