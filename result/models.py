from django.db import models
from course.models import Course
from calendar.models import Semester, SECOND, SEMESTER
from django.urls import reverse
from student.models import Student, CarryOverStudent, RepeatingStudent, LEVEL


# Create your models here.
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


class TakenCourse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='taken_courses')
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


class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    gpa = models.FloatField(null=True)
    cgpa = models.FloatField(null=True)
    semester = models.CharField(max_length=100, choices=SEMESTER)
    session = models.CharField(max_length=100, blank=True, null=True)
    level = models.CharField(max_length=100, choices=LEVEL)
