"""[summary]
    """
from users.models import User
from academic_calendar.models import SEMESTER, Session
from django.db import models
from django.urls import reverse
from student.models import LEVEL

# Create your models here.
class Course(models.Model):
    """[summary]

    Args:
        models ([type]): [description]

    Returns:
        [type]: [description]
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
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course, related_name='allocated_course')
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.lecturer.username
