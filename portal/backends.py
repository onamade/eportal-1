"""
This specific script allows us to define custom authentication backend
for this application. Django by default allows users to be authenticated
with the username name and password but for the sake of this program I needed
to give students the option to login in either with their username or
matric/id number .
"""
from django.contrib.auth.backends import ModelBackend

from .models import Student

class StudentBackend(ModelBackend):
    """
    Custom authentication backend for students that
    inherits from  django modelbackend.
    """
    def authenticate(self, request, **kwargs):
        id_number = kwargs['username']
        password = kwargs['password']
        try:
            student = Student.objects.get(id_number=id_number)
            if student.user.check_password(password) is True:
                return student.user
        except Student.DoesNotExist:
            pass
