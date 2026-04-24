class Student:
    def __init__(self, name, semester, contact):
        self.name = name
        self.semester = semester
        self.contact = contact
        self.semester_result = GradeBook()
        self.GPA = 0


class GradeBook:
    def __init__(self):
        self.subjects = {}


class Subject:
    def __init__(self, name, marks, credit_hrs):
        self.name = name
        self.marks = marks
        self.credit_hrs = credit_hrs
        self.grade_point = self.calculate_grade_points()
        self.gpa_points = self.calculate_quality_points()

    def calculate_grade_points(self):
        marks = self.marks

        if 90 <= marks <= 100:
            return 4.0
        elif 80 <= marks < 90:
            return 3.7
        elif 70 <= marks < 80:
            return 3.3
        elif 60 <= marks < 70:
            return 3.0
        elif 55 <= marks < 60:
            return 2.7
        elif 50 <= marks < 55:
            return 2.3
        elif 45 <= marks < 50:
            return 2.0
        elif 40 <= marks < 45:
            return 1.7
        else:
            return 0.0

    def calculate_quality_points(self):
        return self.credit_hrs * self.grade_point


class StudentManagement:
    def __init__(self):
        self.students_grades = {}

    def add_student(self, name, semester, contact):
        if contact in self.students_grades:
            print(f"{contact} already exists!")
            return

        self.students_grades[contact] = Student(name, semester, contact)

    def add_each_subject_marks(self, contact, **student_marks):
        if contact not in self.students_grades:
            print(f"{contact} not found! Enter registered contact.")
            return

        for subject_code, details in student_marks.items():
            self.students_grades[contact].semester_result.subjects[subject_code] = (
                Subject(
                    details["subject_name"], details["marks"], details["credit_hrs"]
                )
            )

    def calculate_gpa(self, contact):
        if contact not in self.students_grades:
            print(f"{contact} not found! Enter registered contact.")
            return
        results = self.students_grades[contact].semester_result.subjects

        sum_gpa_points = sum(sub.gpa_points for sub in results.values())
        sum_credit_hrs = sum(sub.credit_hrs for sub in results.values())

        self.students_grades[contact].gpa = sum_gpa_points / sum_credit_hrs

        print(f"GPA : {sum_gpa_points/sum_credit_hrs}")

    def rank_student(self):
        sorted_students = sorted(
            self.students_grades.values(), key=lambda student: student.gpa, reverse=True
        )

        for rank, student in enumerate(sorted_students, start=1):
            print(rank, student.name, student.gpa)


sem1_subjects = {
    "CS101": " Introduction to Programming",
    "MA102": "Calculus I",
    "EN103": " Academic English",
    "DS104": "Data Structures",
    "PH105": "Physics Fundamentals",
}

admin = StudentManagement()
admin.add_student("Nischal", 5, 987654321)
admin.add_student("Ramesh", 5, 987654323)

admin.add_each_subject_marks(
    987654321,
    cs101={"marks": 65, "subject_name": sem1_subjects["CS101"], "credit_hrs": 3},
    ma102={"marks": 100, "subject_name": sem1_subjects["MA102"], "credit_hrs": 3},
)


admin.add_each_subject_marks(
    987654323,
    cs101={"marks": 50, "subject_name": sem1_subjects["CS101"], "credit_hrs": 3},
    ma102={"marks": 94, "subject_name": sem1_subjects["MA102"], "credit_hrs": 3},
)


admin.calculate_gpa(987654321)
admin.calculate_gpa(987654323)


admin.rank_student()
