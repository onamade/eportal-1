from celery import task
from django.core.mail import send_mail

from .models import Student
from .models import User


@task
def default_password(id_number, pwd):
    """
    Task to send auto-generated passwords to student's e-mail
    """
    student = Student.objects.get(id_number=id_number)
    subject = f'Matric Number: {id_number}'
    message = f'Dear {student.user.first_name},\n\n' \
              f'You have been successfully Registered to University Eportal.' \
              f'Your Matric Number is: {id_number}' \
              f'Your Password is: {pwd}'
    mail_sent = send_mail(
        subject, message, 'noreply@aueportal.com', [student.user.email])

    return mail_sent

@task
def default_password_staff(username, pwd):
    """
    Task to send auto-generated passwords to staff's e-mail
    """
    staff = User.objects.get(username=username)
    subject = f'Username: {username}'
    message = f'Dear {staff.first_name},\n\n' \
              f'You have been successfully Registered to University Eportal.' \
              f'Your Username is: {username}' \
              f'Your Password is: {pwd}'
    mail_sent = send_mail(
        subject, message, 'noreply@aueportal.com', [staff.email])

    return mail_sent
