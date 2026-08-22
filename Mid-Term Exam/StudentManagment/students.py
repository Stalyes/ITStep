import os

class Student:
    def __init__(self, name, roll_number, grade):
        if not name or not isinstance(name, str):
            raise ValueError("Name must be a non-empty string")
        if not isinstance(roll_number, int) or roll_number <= 0:
            raise ValueError("Roll number must be a positive integer")
        if not isinstance(grade, str) or len(grade) != 1:
            raise ValueError("Grade must be a single character")
        
        self.name = name
        self.roll_number = roll_number
        self.grade = grade
    
    def __str__(self):
        return f"{self.name},{self.roll_number},{self.grade}"

class StudentManager:
    def __init__(self, filename="students.txt"):
        self.filename = filename
        self.students = []
        self.load_students()
    
    @staticmethod
    def validate_grade(grade):
        grade = grade.strip().upper()
        if len(grade) == 1 and grade in "ABCDEF":
            return grade
        return None
    
    def load_students(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            parts = line.split(',')
                            if len(parts) == 3:
                                self.students.append(Student(parts[0], int(parts[1]), parts[2]))
            except (ValueError, IndexError) as e:
                print(f"Error loading students: {e}")
    
    def save_students(self):
        with open(self.filename, 'w') as f:
            for student in self.students:
                f.write(f"{student}\n")
    
    def add_student(self):
        try:
            name = input("Name: ").strip()
            if not name:
                print("Name cannot be empty")
                return
            
            while True:
                try:
                    roll_number = int(input("Roll Number: "))
                    if roll_number <= 0:
                        print("Roll number must be positive")
                        continue
                    break
                except ValueError:
                    print("Invalid roll number")
            
            while True:
                grade = self.validate_grade(input("grade a-f: "))
                if grade is None:
                    print("Invalid grade")
                    continue
                break
            
            self.students.append(Student(name, roll_number, grade))
            self.save_students()
            print("Added")
        except Exception as e:
            print(f"Error: {e}")
    
    def view_all_students(self):
        if not self.students:
            print("No students found")
            return
        for student in self.students:
            print(f"Name: {student.name}, Roll: {student.roll_number}, Grade: {student.grade}")
    
    def search_by_roll_number(self):
        try:
            roll_number = int(input("Roll Number: "))
            for student in self.students:
                if student.roll_number == roll_number:
                    print(f"Name: {student.name}, Roll: {student.roll_number}, Grade: {student.grade}")
                    return
            print("Not found")
        except ValueError:
            print("Invalid roll number")
    
    def update_grade(self):
        try:
            roll_number = int(input("Roll Number: "))
            for student in self.students:
                if student.roll_number == roll_number:
                    while True:
                        grade = self.validate_grade(input("New Grade (A-F): "))
                        if grade is None:
                            print("Invalid grade")
                            continue
                        break
                    student.grade = grade
                    self.save_students()
                    print("Updated")
                    return
            print("Not found")
        except ValueError:
            print("Invalid roll number")

def main():
    manager = StudentManager()
    while True:
        print("\n1. add student")
        print("2. view all students")
        print("3. roll number search")
        print("4. update grade")
        print("0. exit")
        choice = input("Choice: ").strip()
        
        if choice == '1':
            manager.add_student()
        elif choice == '2':
            manager.view_all_students()
        elif choice == '3':
            manager.search_by_roll_number()
        elif choice == '4':
            manager.update_grade()
        elif choice == '0':
            break
        else:
            print("incorrect keybind")

if __name__ == "__main__":
    main()