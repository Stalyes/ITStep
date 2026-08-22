import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from school.models import Course, Lecturer, Student

Student.objects.all().delete()
Course.objects.all().delete()
Lecturer.objects.all().delete()

lecturer_data = [
    ("Maya", "Kandelaki", "maya.kandelaki@example.com", "Computer Science"),
    ("Liam", "Carter", "liam.carter@example.com", "Web Development"),
    ("Elene", "Javakhishvili", "elene.javakhishvili@example.com", "Data Systems"),
]
lecturers = [
    Lecturer.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        department=department,
    )
    for first_name, last_name, email, department in lecturer_data
]

course_data = [
    ("Python Foundations", "Programming fundamentals", 4, lecturers[0]),
    ("Web Interfaces", "Modern frontend principles", 5, lecturers[1]),
    ("Data Modeling", "Relational data concepts", 5, lecturers[2]),
    ("Algorithms", "Problem solving and complexity", 6, lecturers[0]),
    ("Backend Services", "Building reliable web services", 6, lecturers[1]),
]
courses = [
    Course.objects.create(
        title=title,
        description=description,
        credits=credits,
        lecturer=lecturer,
    )
    for title, description, credits, lecturer in course_data
]

student_data = [
    ("Tako", "Maisuradze", "tako.student@example.com", [0, 1]),
    ("Gio", "Beridze", "gio.student@example.com", [1, 2]),
    ("Nana", "Lomidze", "nana.student@example.com", [2, 3]),
    ("Saba", "Kiknadze", "saba.student@example.com", [3, 4]),
    ("Mariam", "Gelashvili", "mariam.student@example.com", [0, 2]),
    ("Dato", "Chikovani", "dato.student@example.com", [1, 3]),
    ("Ana", "Tsiklauri", "ana.student@example.com", [2, 4]),
    ("Luka", "Maisuradze", "luka.student@example.com", [0, 4]),
    ("Salome", "Japaridze", "salome.student@example.com", [0, 1, 3]),
    ("Irakli", "Lomidze", "irakli.student@example.com", [1, 2, 4]),
]
for first_name, last_name, email, course_indexes in student_data:
    student = Student.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
    )
    student.courses.set(courses[index] for index in course_indexes)

print("--- All students ---")
for student in Student.objects.all():
    print(student)

print("\n--- All courses ---")
for course in Course.objects.select_related("lecturer"):
    print(f"{course.title} | {course.lecturer}")

print("\n--- All lecturers ---")
for lecturer in Lecturer.objects.all():
    print(lecturer)

student_by_id = Student.objects.get(id=Student.objects.first().id)
print(f"\nStudent by ID: {student_by_id}")

course_by_name = Course.objects.get(title="Python Foundations")
print(f"Course by title: {course_by_name}")

for course in lecturers[0].courses.all():
    print(f"Maya's course: {course.title}")

for student in courses[0].students.all():
    print(f"Python student: {student}")

selected_student = Student.objects.get(email="tako.student@example.com")
for course in selected_student.courses.all():
    print(f"Tako's course: {course.title}")

selected_student.first_name = "Tamuna"
selected_student.save()

lecturers[0].last_name = "Kandeladze"
lecturers[0].save()

courses[0].title = "Advanced Python"
courses[0].save()

selected_student.courses.add(courses[2])
selected_student.courses.remove(courses[1])
selected_student.courses.remove(courses[0])
selected_student.courses.add(courses[4])

courses[1].lecturer = lecturers[2]
courses[1].save()

Student.objects.get(email="irakli.student@example.com").delete()
Course.objects.get(title="Algorithms").delete()
Lecturer.objects.get(email="liam.carter@example.com").delete()
selected_student.courses.clear()

print("\n--- Final counts ---")
print(f"Students: {Student.objects.count()}")
print(f"Courses: {Course.objects.count()}")
print(f"Lecturers: {Lecturer.objects.count()}")
