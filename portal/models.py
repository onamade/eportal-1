#######################################################################
#  Models that contains the details and structre of data that is used
#  throughout the database for this application.
#######################################################################

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.urls import reverse

from .validators import ASCIIUsernameValidator

LEVEL = (
    ("100", 100),
    ("200", 200),
    ("300", 300),
    ("400", 400),
    ("500", 500),
)

FACULTY = (
    ("FOS", "FOS"),
    ("FOE", "FOE"),
    ("FBMS", "FBMS"),
    ("FBSS", "FBSS"),
    ("FOA", "FOA"),
    ("FOL", "FOL"),
)

DEPARTMENT = (
    ("COMPUTER SCIENCE", "COMPUTER SCIENCE"),
    ("MATHEMATICS", "MATHEMATICS"),
    ("PHYSICS", "PHYSICS"),
    ("CHEMISTRY", "CHEMISTRY"),
    ("BIOLOGICAL SCIENCE", "BIOLOGICAL SCIENCE"),
    ("INDUSTRIAL CHEMISTRY", "INDUSTRIAL CHEMISTRY"),
    ("MICROBIOLOGY", "MICROBIOLOGY"),
    ("BIOCHEMISTRY", "BIOCHEMISTRY"),
    ("COMPUTER INFORMATION SYSTEM", "COMPUTER INFORMATION SYSTEM"),
    ("AGRICULTURAL ENGINEERING", "AGRICULTURAL ENGINEERING"),
    ("CIVIL ENGINEERING", "CIVIL ENGINEERING"),
    ("ELECTRONIC & ELECTRICAL ENGINEERING", "ELECTRONIC & ELECTRICAL ENGINEERING"),
    ("MECHANICAL ENGINEERING", "MECHANICAL ENGINEERING"),
    ("ACCOUNTING", "ACCOUNTING"),
    ("BUSINESS ADMINISTRATION", "BUSINESS ADMINISTRATION"),
    ("ECONOMICS", "ECONOMICS"),
    ("MASS COMMUNICATION", "MASS COMMUNICATION"),
    ("POLITICAL SCIENCE", "POLITICAL SCIENCE"),
    ("PUBLIC ADMINISTRATION", "PUBLIC ADMINISTRATION"),
    ("LIBRARY INFORMATION SCIENCE", "LIBRARY INFORMATION SCIENCE"),
    ("ANATOMY", "ANATOMY"),
    ("NURSING", "NURSING"),
    ("PUBLIC HEALTH", "PUBLIC HEALTH"),
    ("PHYSIOLOGY", "PHYSIOLOGY"),
    ("RELIGIOUS STUDIES", "RELIGIOUS STUDIES"),
    ("HISTORY & INTERNATIONAL STUDIES", "HISTORY & INTERNATIONAL STUDIES"),
    ("LANGUAGE & LITERARY STUDIES", "LANGUAGE & LITERARY STUDIES"),
    ("LAW", "LAW"),
)

FIRST = "First"
SECOND = "Second"

SEMESTER = (
    (FIRST, "First"),
    (SECOND, "Second"),
)

A = "A"
B = "B"
C = "C"
D = "D"
F = "F"
PASS = "PASS"
FAIL = "FAIL"

GRADE = (
    (A, 'A'),
    (B, 'B'),
    (C, 'C'),
    (D, 'D'),
    (F, 'F'),
)

COMMENT = (
    (PASS, "PASS"),
    (FAIL, "FAIL"),
)


class Session(models.Model):
    """
    Academic session database table.
    """
    session = models.CharField(max_length=200, unique=True)
    is_current_session = models.BooleanField(
        default=False, blank=True, null=True)
    next_session_begins = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.session


class Semester(models.Model):
    """
    Semster database table.
    """
    semester = models.CharField(max_length=10, choices=SEMESTER, blank=True)
    is_current_semester = models.BooleanField(
        default=False, blank=True, null=True)
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, blank=True, null=True)
    next_semester_begins = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.semester


class User(AbstractUser):
    """
    Custom User model that extends the functionality of the
    default django user model. This is the User
    database table.
    """
    is_student = models.BooleanField(default=False)
    is_lecturer = models.BooleanField(default=False)
    phone = models.CharField(max_length=60, blank=True, null=True)
    address = models.CharField(max_length=60, blank=True, null=True)
    picture = models.ImageField(upload_to="pictures/", blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    username_validator = ASCIIUsernameValidator()

    def get_picture(self):
        no_picture = settings.STATIC_URL + 'img/img_avatar.png'
        try:
            return self.picture.url
        except:
            return no_picture

    def get_full_name(self):
        full_name = self.username
        if self.first_name and self.last_name:
            full_name = self.first_name + " " + self.last_name
        return full_name


class Student(models.Model):
    """
    Student Database Table
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_number = models.CharField(max_length=20, unique=True)
    level = models.CharField(choices=LEVEL, max_length=3)
    faculty = models.CharField(choices=FACULTY, max_length=4)
    department = models.CharField(choices=DEPARTMENT, max_length=40)

    def __str__(self):
        return self.id_number

    def get_absolute_url(self):
        return reverse('profile')


class Course(models.Model):
    """
    Course database table
    """
    courseTitle = models.CharField(max_length=200)
    courseCode = models.CharField(max_length=200, unique=True)
    courseUnit = models.CharField(max_length=200)
    description = models.TextField(max_length=200, blank=True)
    level = models.CharField(choices=LEVEL, max_length=3, blank=True)
    semester = models.CharField(choices=SEMESTER, max_length=200)
    is_elective = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return self.courseCode + " (" + self.courseTitle + ")"

    def get_absolute_url(self):
        return reverse('course_list', kwargs={'pk': self.pk})

    def get_total_unit(self):
        t = 0
        total = Course.objects.all()
        for i in total:
            t += i
        return i


class CourseAllocation(models.Model):
    """
    CourseAllocation database table
    """
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course, related_name='allocated_course')
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.lecturer.username


class CarryOverStudent(models.Model):
    """
    CarryOverStudents database table
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.CharField(
        max_length=100, choices=SEMESTER, blank=True, null=True)
    session = models.CharField(max_length=100, blank=True, null=True)
    level = models.CharField(
        choices=LEVEL, max_length=10, blank=True, null=True)

    def __str__(self):
        return self.student.id_number


class RepeatingStudent(models.Model):
    """
    RepeatingStudent database table.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    level = models.CharField(max_length=100, choices=LEVEL)
    session = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.student.id_number


class TakenCourse(models.Model):
    """
    Database table for keeping records of students that has
    registered for courses and also keep recorsds of their CA and exams
    score once its available.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='taken_courses')
    ca = models.PositiveIntegerField(blank=True, null=True, default=0)
    exam = models.PositiveIntegerField(blank=True, null=True, default=0)
    total = models.PositiveIntegerField(blank=True, null=True, default=0)
    grade = models.CharField(choices=GRADE, max_length=1, blank=True)
    comment = models.CharField(choices=COMMENT, max_length=200, blank=True)

    def get_absolute_url(self):
        return reverse('update_score', kwargs={'pk': self.pk})

    def get_total(self, ca, exam):
        return int(ca) + int(exam)

    def get_grade(self, ca, exam):
        total = int(ca) + int(exam)
        if total >= 70:
            grade = A
        elif total >= 60:
            grade = B
        elif total >= 50:
            grade = C
        elif total >= 45:
            grade = D
        else:
            grade = F
        return grade

    def get_nursing_grade(self, ca, exam):
        total = int(ca) + int(exam)
        if total >= 70:
            grade = A
        elif total >= 60:
            grade = B
        elif total >= 50:
            grade = C
        else:
            grade = F
        return grade

    def get_comment(self, grade):
        if not grade == "F":
            comment = PASS
        else:
            comment = FAIL
        return comment

    def carry_over(self, grade):
        if grade == F:
            CarryOverStudent.objects.get_or_create(
                student=self.student, course=self.course)
        else:
            try:
                CarryOverStudent.objects.get(
                    student=self.student, course=self.course).delete()
            except:
                pass

    def is_repeating(self):
        count = CarryOverStudent.objects.filter(student__id=self.student.id)
        units = 0
        for i in count:
            units += int(i.course.courseUnit)
        if count.count() >= 6 or units >= 16:
            RepeatingStudent.objects.get_or_create(
                student=self.student, level=self.student.level)
        else:
            try:
                RepeatingStudent.objects.get(
                    student=self.student, level=self.student.level).delete()
            except:
                pass
    def calculate_gpa(self, total_unit_in_semester):
        current_semester = Semester.objects.get(is_current_semester=True)
        student = TakenCourse.objects.filter(
            student=self.student, course__level=self.student.level, course__semester=current_semester)
        p = 0
        point = 0
        for i in student:
            courseUnit = i.course.courseUnit
            if i.grade == A:
                point = 5
            elif i.grade == B:
                point = 4
            elif i.grade == C:
                point = 3
            elif i.grade == D:
                point = 2
            else:
                point = 0
            p += int(courseUnit) * point
        try:
            gpa = (p / total_unit_in_semester)
            return round(gpa, 1)
        except ZeroDivisionError:
            return 0

    def calculate_cgpa(self):
        current_semester = Semester.objects.get(is_current_semester=True)
        previousResult = Result.objects.filter(
            student__id=self.student.id, level__lt=self.student.level)
        previousCGPA = 0
        for i in previousResult:
            if i.cgpa is not None:
                previousCGPA += i.cgpa
        cgpa = 0
        if str(current_semester) == SECOND:

            taken_courses = TakenCourse.objects.filter(
                student=self.student, student__level=self.student.level)
            p = 0
            point = 0
            TCU = 0
            for i in taken_courses:
                TCU += int(i.course.courseUnit)
                courseUnit = i.course.courseUnit
                if i.grade == A:
                    point = 5
                elif i.grade == B:
                    point = 4
                elif i.grade == C:
                    point = 3
                elif i.grade == D:
                    point = 2
                else:
                    point = 0
                p += int(courseUnit) * point
            try:
                cgpa = (p / TCU)
                return round(cgpa, 2)
            except ZeroDivisionError:
                return 0
        return


class Result(models.Model):
    """
    Result Dtabase Table that keeps record of the,
    Final result of students who have taken courses and
    and have CAs and exam scores in their records.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    gpa = models.FloatField(null=True)
    cgpa = models.FloatField(null=True)
    semester = models.CharField(max_length=100, choices=SEMESTER)
    session = models.CharField(max_length=100, blank=True, null=True)
    level = models.CharField(max_length=100, choices=LEVEL)
