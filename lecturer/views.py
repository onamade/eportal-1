from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from users.decorators import lecturer_required
from calendar.models import Session, Semester
from course.models import Course
from result.models import TakenCourse, Result


# Create your views here.
@login_required
@lecturer_required
def add_score(request):
    """
    Shows a page where a lecturer will select a course allocated to him for score entry.
    in a specific semester and session

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

    if request.method == 'POST':
        ids = ()
        data = request.POST.copy()
        data.pop('csrfmiddlewaretoken', None)  # remove csrf_token
        for key in data.keys():
            # gather all the all students id (i.e the keys) in a tuple
            ids = ids + (str(key), )
        for s in range(0, len(
                ids)):  # iterate over the list of student ids gathered above
            student = TakenCourse.objects.get(id=ids[s])
            courses = Course.objects.filter(
                level=student.student.level).filter(
                    semester=current_semester
                )  # all courses of a specific level in current semester
            total_unit_in_semester = 0
            for i in courses:
                if i == courses.count():
                    break
                else:
                    total_unit_in_semester += int(i.courseUnit)
            # get list of score for current student in the loop
            score = data.getlist(ids[s])
            # subscript the list to get the fisrt value > ca score
            ca = score[0]
            exam = score[1]  # do thesame for exam score
            # get the current student data
            obj = TakenCourse.objects.get(pk=ids[s])
            obj.ca = ca  # set current student ca score
            obj.exam = exam  # set current student exam score
            obj.total = obj.get_total(ca=ca, exam=exam)
            obj.grade = obj.get_grade(ca=ca, exam=exam)
            obj.comment = obj.get_comment(obj.grade)
            obj.carry_over(obj.grade)
            obj.is_repeating()
            obj.save()
            gpa = obj.calculate_gpa(total_unit_in_semester)
            cgpa = obj.calculate_cgpa()
            try:
                a = Result.objects.get(student=student.student,
                                       semester=current_semester,
                                       level=student.student.level)
                a.gpa = gpa
                a.cgpa = cgpa
                a.save()
            except:
                Result.objects.get_or_create(student=student.student,
                                             gpa=gpa,
                                             semester=current_semester,
                                             level=student.student.level)
        messages.success(request, 'Successfully Recorded! ')
        return HttpResponseRedirect(
            reverse_lazy('add_score_for', kwargs={'id': id}))
    return HttpResponseRedirect(
        reverse_lazy('add_score_for', kwargs={'id': id}))
