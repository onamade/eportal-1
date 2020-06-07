import weasyprint

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings


from users.decorators import student_required, lecturer_required
from student.models import Student
from course.models import Course
from result.models import TakenCourse, Result
from calendar.models import Semester

# Create your views here.
@login_required
@student_required
def course_registration(request):
    if request.method == 'POST':
        ids = ()
        data = request.POST.copy()
        data.pop('csrfmiddlewaretoken', None)  # remove csrf_token
        for key in data.keys():
            ids = ids + (str(key), )
        for s in range(0, len(ids)):
            student = Student.objects.get(user__pk=request.user.id)
            course = Course.objects.get(pk=ids[s])
            obj = TakenCourse.objects.create(student=student, course=course)
            obj.save()
            messages.success(request, 'Courses Registered Successfully!')
        return redirect('course_registration')
    else:
        student = Student.objects.get(user__pk=request.user.id)
        taken_courses = TakenCourse.objects.filter(
            student__user__id=request.user.id)
        t = ()
        for i in taken_courses:
            t += (i.course.pk, )
        current_semester = Semester.objects.get(is_current_semester=True)
        courses = Course.objects.filter(level=student.level).exclude(id__in=t)
        all_courses = Course.objects.filter(level=student.level)

        no_course_is_registered = False  # Check if no course is registered
        all_courses_are_registered = False

        registered_courses = Course.objects.filter(level=student.level).filter(
            id__in=t)
        if registered_courses.count(
        ) == 0:  # Check if number of registered courses is 0
            no_course_is_registered = True

        if registered_courses.count() == all_courses.count():
            all_courses_are_registered = True

        total_first_semester_unit = 0
        total_sec_semester_unit = 0
        total_registered_unit = 0
        for i in courses:
            if i.semester == "First":
                total_first_semester_unit += int(i.courseUnit)
            if i.semester == "Second":
                total_sec_semester_unit += int(i.courseUnit)
        for i in registered_courses:
            total_registered_unit += int(i.courseUnit)
        context = {
            "all_courses_are_registered": all_courses_are_registered,
            "no_course_is_registered": no_course_is_registered,
            "current_semester": current_semester,
            "courses": courses,
            "total_first_semester_unit": total_first_semester_unit,
            "total_sec_semester_unit": total_sec_semester_unit,
            "registered_courses": registered_courses,
            "total_registered_unit": total_registered_unit,
            "student": student,
        }
        return render(request, 'course/course_registration.html', context)


@login_required
@student_required
def course_drop(request):
    if request.method == 'POST':
        ids = ()
        data = request.POST.copy()
        data.pop('csrfmiddlewaretoken', None)  # remove csrf_token
        for key in data.keys():
            ids = ids + (str(key), )
        for s in range(0, len(ids)):
            student = Student.objects.get(user__pk=request.user.id)
            course = Course.objects.get(pk=ids[s])
            obj = TakenCourse.objects.get(student=student, course=course)
            obj.delete()
            messages.success(request, 'Successfully Dropped!')
        return redirect('course_registration')


@login_required
@student_required
def view_result(request):
    student = Student.objects.get(user__pk=request.user.id)
    current_semester = Semester.objects.get(is_current_semester=True)
    courses = TakenCourse.objects.filter(student__user__pk=request.user.id,
                                         course__level=student.level)
    result = Result.objects.filter(student__user__pk=request.user.id)
    current_semester_grades = {}

    previousCGPA = 0
    previousLEVEL = 0
    currentCGPA = 0
    # TODO : implement previousCGPA funtionality later
    try:
        a = Result.objects.get(student__user__pk=request.user.id,
                               level=student.level,
                               semester="Second")
        current_CGPA = a.cgpa
    except:
        current_CGPA = 0

    context = {
        "courses": courses,
        "result": result,
        "student": student,
        "previousCGPA": previousCGPA,
        "currentCGPA": current_CGPA,
    }

    return render(request, 'students/view_results.html', context)


@login_required
@student_required
def course_registration_pdf(request):
    """View to handle WeasyPrint PDF for student Course Registration

    Args:
        request ([type]): [description]

    Returns:
        [type]: [description]
    """
    student = Student.objects.get(user__pk=request.user.id)
    taken_courses = TakenCourse.objects.filter(
        student__user__id=request.user.id)
    t = ()
    for i in taken_courses:
        t += (i.course.pk, )
        registered_courses = Course.objects.filter(level=student.level).filter(
            id__in=t)
        total_registered_unit = 0
        for i in registered_courses:
            total_registered_unit += int(i.courseUnit)
    html = render_to_string(
        'course/pdf.html', {
            "student": student,
            "registered_courses": registered_courses,
            "total_registered_unit": total_registered_unit,
        })
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = f'filname=student_{student.id_number}.pdf'
    weasyprint.HTML(string=html).write_pdf(
        response,
        stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')])
    return response
