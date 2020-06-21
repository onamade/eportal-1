import csv
import io

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from users.decorators import lecturer_required
from academic_calendar.models import Session, Semester
from course.models import Course
from result.models import TakenCourse, Result
from student.models import Student


# Create your views here.
@login_required
@lecturer_required
def add_score(request):
    """Shows a page where a lecturer will select a course allocated to him for
    score entry in a specific semester and session

    """
    current_session = Session.objects.get(is_current_session=True)
    current_semester = get_object_or_404(Semester,
                                         is_current_semester=True,
                                         session=current_session)
    semester = Course.objects.filter(
        allocated_course__lecturer__pk=request.user.id,
        semester=current_semester)
    courses = Course.objects.filter(
        allocated_course__lecturer__pk=request.user.id).filter(
        semester=current_semester)
    context = {
        "courses": courses,
    }
    return render(request, 'result/add_score.html', context)


@login_required
@lecturer_required
def add_score_for(request, id):
    """Shows a page where a lecturer will add score for studens that are taking courses allocated to him
    in a specific semester and session
    """
    current_semester = Semester.objects.get(is_current_semester=True)
    if request.method == 'GET':
        courses = Course.objects.filter(
            allocated_course__lecturer__pk=request.user.id).filter(
            semester=current_semester)
        course = Course.objects.get(pk=id)
        students = TakenCourse.objects.filter(
            course__allocated_course__lecturer__pk=request.user.id).filter(
            course__id=id).filter(course__semester=current_semester)
        context = {
            "courses": courses,
            "course": course,
            "students": students,
        }
        return render(request, 'result/add_score_for.html', context)
    if request.method == "POST":
        ids = ()
        cas = ()
        exams = ()
        csv_file = request.FILES['file']
        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        next(io_string)
        for column in csv.reader(io_string, delimiter=',', quotechar="|"):
            ids = ids + (column[0],)
            cas = cas + (column[1],)
            exams = exams + (column[2],)

        for s in range(0, len(ids)):
            student = TakenCourse.objects.get(
                student__id_number=ids[s], course__id=id, )
            # nursing = Student.objects.get(department='NURSING')
            courses = TakenCourse.objects.filter(
                student__id_number=ids[s], course__semester=current_semester)
            total_unit_in_semester = 0
            for i in courses:
                if i == courses.count():
                    break
                else:
                    total_unit_in_semester += int(i.course.courseUnit)
            student.ca = cas[s]
            student.exam = exams[s]
            student.total = student.get_total(ca=student.ca, exam=student.exam)
            if student.student.department == 'NURSING' and not student.course.courseCode.startswith('GES'):
                student.grade = student.get_nursing_grade(
                    ca=student.ca, exam=student.exam)
            else:
                student.grade = student.get_grade(
                    ca=student.ca, exam=student.exam)
            student.comment = student.get_comment(student.grade)
            student.carry_over(student.grade)
            student.is_repeating()
            student.save()
            gpa = student.calculate_gpa(total_unit_in_semester)
            cgpa = student.calculate_cgpa()

            try:
                a = Result.objects.get(student=student.student,
                                       semester=current_semester,
                                       level=student.student.level)
                a.gpa = gpa
                a.cgpa = cgpa
                a.save()
            except:
                Result.objects.get_or_create(student=student.student,
                                             semester=current_semester,
                                             level=student.student.level,
                                             gpa=gpa,
                                             cgpa=cgpa,
                                             session=current_semester.session)
        messages.success(request, 'Successfully Uploaded and Recorded')
        return HttpResponseRedirect(
            reverse_lazy('add_score_for', kwargs={'id': id}))
    return HttpResponseRedirect(
        reverse_lazy('add_score_for', kwargs={'id': id})
    )
