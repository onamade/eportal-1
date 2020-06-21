from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

from student.models import Student

class StudentBackend(ModelBackend):

    def authenticate(self, request, **kwargs):
        id_number = kwargs['username']
        password = kwargs['password']
        try:
            student = Student.objects.get(id_number=id_number)
            if student.user.check_password(password) is True:
                return student.user
        except Student.DoesNotExist:
            pass