"""[summary]

    Returns:
        [type]: [description]
    """
from django.db import models

FIRST = "First"
SECOND = "Second"

SEMESTER = (
    (FIRST, "First"),
    (SECOND, "Second"),
)

# Create your models here.
class Session(models.Model):
    """[summary]

    Args:
        models ([type]): [description]

    Returns:
        [type]: [description]
    """
    session = models.CharField(max_length=200, unique=True)
    is_current_session = models.BooleanField(
        default=False, blank=True, null=True)
    next_session_begins = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.session


class Semester(models.Model):
    """[summary]

    Args:
        models ([type]): [description]

    Returns:
        [type]: [description]
    """
    semester = models.CharField(max_length=10, choices=SEMESTER, blank=True)
    is_current_semester = models.BooleanField(
        default=False, blank=True, null=True)
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, blank=True, null=True)
    next_semester_begins = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.semester
