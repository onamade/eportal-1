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


# Create your models here.
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_number = models.CharField(max_length=20, unique=True)
    level = models.CharField(choices=LEVEL, max_length=3)
    faculty = models.CharField(choices=FACULTY, max_length=4)
    department = models.CharField(choices=DEPARTMENT, max_length=40)

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
