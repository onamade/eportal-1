from django.db import models
from users.models import User
from django.urls import reverse
from academic_calendar.models import SEMESTER

LEVEL = (
    ("100", 100),
    ("200", 200),
    ("300", 300),
    ("400", 400),
    ("500", 500),
)

# Create your models here.
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_number = models.CharField(max_length=20, unique=True)
    level = models.CharField(choices=LEVEL, max_length=3)

    def __str__(self):
        return self.id_number

    def get_absolute_url(self):
        return reverse('profile')

from course.models import Course
class CarryOverStudent(models.Model):
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
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    level = models.CharField(max_length=100, choices=LEVEL)
    session = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.student.id_number

