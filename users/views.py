"""[summary]

    Returns:
        [type]: [description]
    """
from academic_calendar.models import Semester
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from student.models import Student, CarryOverStudent, RepeatingStudent
from course.models import Course
from result.models import TakenCourse, Result
from .decorators import lecturer_required, admin_required
from .forms import ProfileForm
from .models import User


@login_required
def home(request):
    """
    Shows our dashboard containing number of students, courses, lecturers,
    repating students,
    carry over students and 1st class students in an interactive graph
    """
    students = Student.objects.all().count()
    staff = User.objects.filter(is_lecturer=True).count()
    courses = Course.objects.all().count()
    current_semester = Semester.objects.get(is_current_semester=True)
    no_of_1st_class_students = Result.objects.filter(cgpa__gte=4.5).count()
    no_of_carry_over_students = CarryOverStudent.objects.all().count()
    no_of_students_to_repeat = RepeatingStudent.objects.all().count()

    context = {
        "no_of_students": students,
        "no_of_staff": staff,
        "no_of_courses": courses,
        "no_of_1st_class_students": no_of_1st_class_students,
        "no_of_students_to_repeat": no_of_students_to_repeat,
        "no_of_carry_over_students": no_of_carry_over_students,
        current_semester: current_semester,
    }

    return render(request, 'result/home.html', context)


@login_required
def profile(request):
    """ Show profile of any user that fire out the request """
    current_semester = Semester.objects.get(is_current_semester=True)
    if request.user.is_lecturer:
        courses = Course.objects.filter(
            allocated_course__lecturer__pk=request.user.id).filter(
                semester=current_semester)
        return render(request, 'account/profile.html', {
            "courses": courses,
        })
    elif request.user.is_student:
        level = Student.objects.get(user__pk=request.user.id)
        courses = TakenCourse.objects.filter(student__user__id=request.user.id,
                                             course__level=level.level)
        context = {
            'courses': courses,
            'level': level,
        }
        return render(request, 'account/profile.html', context)
    else:
        staff = User.objects.filter(is_lecturer=True)
        return render(request, 'account/profile.html', {"staff": staff})


@login_required
def user_profile(request, id):
    """ Show profile of any selected user """
    if request.user.id == id:
        return redirect("/profile/")

    current_semester = Semester.objects.get(is_current_semester=True)
    user = User.objects.get(pk=id)
    if user.is_lecturer:
        courses = Course.objects.filter(
            allocated_course__lecturer__pk=id).filter(
                semester=current_semester)
        context = {
            "user": user,
            "courses": courses,
        }
        return render(request, 'account/user_profile.html', context)
    elif user.is_student:
        level = Student.objects.get(user__pk=id)
        courses = TakenCourse.objects.filter(student__user__id=id,
                                             course__level=level.level)
        context = {
            "user_type": "student",
            'courses': courses,
            'level': level,
            'user': user,
        }
        return render(request, 'account/user_profile.html', context)
    else:
        context = {"user": user, "user_type": "superuser"}
        return render(request, 'account/user_profile.html', context)


@login_required
@lecturer_required
@admin_required
def profile_update(request):
    """ Check if the fired request is a POST then grap changes and update the records otherwise we show an empty form """
    user = request.user.id
    user = User.objects.get(pk=user)
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            # user.first_name = form.cleaned_data.get('first_name')
            # user.last_name = form.cleaned_data.get('last_name')
            # user.email = form.cleaned_data.get('email')
            # user.phone = form.cleaned_data.get('phone')
            # user.address = form.cleaned_data.get('address')
            if request.FILES:
                user.picture = request.FILES['picture']
            user.save()
            messages.success(request, 'Your profile was successfully edited.')
            return redirect("/profile/")
    else:
        form = ProfileForm(instance=user,
                           initial={
                            #    'firstname': user.first_name,
                            #    'lastname': user.last_name,
                            #    'email': user.email,
                            #    'phone': user.phone,
                               'picture': user.picture,
                           })

    return render(request, 'account/profile_update.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request,
                             'Your password was successfully updated!')
        else:
            messages.error(request, 'Please correct the errors below. ')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'account/change_password.html', {
        'form': form,
    })


@login_required
@lecturer_required
def result_sheet_pdf_view(request, id): # TODO: print result with weasyprint
    """function to print result in pdf format

    Args:
        request ([type]): [description]
        id ([type]): [description]
    """
    pass