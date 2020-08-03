import csv
import io
import weasyprint

from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse_lazy

from .tasks import default_password, default_password_staff
from .decorators import lecturer_required, admin_required, student_required
from .forms import (
    ProfileForm, StaffAddForm, StudentAddForm, SessionForm,
    SemesterForm, CourseAddForm, CourseAllocationForm)
from .models import (
    User, Student, CarryOverStudent, RepeatingStudent, Course,
    TakenCourse, Result, Semester, CourseAllocation, Session
)

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
    """ 
    Check if the fired request is a POST then grap changes and
    update the records otherwise we show an empty form.
    """
    user = request.user.id
    user = User.objects.get(pk=user)
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            if request.FILES:
                user.picture = request.FILES['picture']
            user.save()
            messages.success(request, 'Your profile was successfully edited.')
            return redirect("/profile/")
    else:
        form = ProfileForm(instance=user,
                           initial={
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

def get_chart(request, *args, **kwargs):
    all_query_score = ()
    levels = (100, 200, 300, 400, 500)  # all the levels in the department

    # iterate through the levels above
    for i in levels:
        # gather all the courses registered by the students of the current
        # level in the loop
        all_query_score += (TakenCourse.objects.filter(student__level=i), )

    # for level #100
    first_level_total = 0

    # get the total score for all the courses registered by the students of
    # this level
    for i in all_query_score[0]:
        first_level_total += i.total

    first_level_avg = 0
    if not all_query_score[0].count() == 0:
        # calculate the average of all the students of this level
        first_level_avg = first_level_total / all_query_score[0].count()

    # do same  as above for # 200 Level students
    second_level_total = 0
    for i in all_query_score[1]:
        second_level_total += i.total
    second_level_avg = 0
    if not all_query_score[1].count() == 0:
        second_level_avg = second_level_total / all_query_score[1].count()

    # do same  as above for # 300 Level students
    third_level_total = 0
    for i in all_query_score[2]:
        third_level_total += i.total
    third_level_avg = 0
    if not all_query_score[2].count() == 0:
        third_level_avg = third_level_total / all_query_score[2].count()

    # do same  as above for # 400 Level students
    fourth_level_total = 0
    for i in all_query_score[3]:
        fourth_level_total += i.total
    fourth_level_avg = 0
    if not all_query_score[3].count() == 0:
        fourth_level_avg = fourth_level_total / all_query_score[3].count()

    # do same  as above for # 500 Level students
    fifth_level_total = 0
    for i in all_query_score[4]:
        fifth_level_total += i.total
    fifth_level_avg = 0
    if not all_query_score[4].count() == 0:
        fifth_level_avg = fifth_level_total / all_query_score[4].count()

    labels = ["100 Level", "200 Level", "300 Level", "400 Level", "500 Level"]
    default_level_average = [
        first_level_avg, second_level_avg, third_level_avg, fourth_level_avg,
        fifth_level_avg
    ]
    average_data = {
        "labels": labels,
        "default_level_average": default_level_average,
    }
    return JsonResponse(average_data)


@login_required
@lecturer_required
def course_list(request):
    """ Show list of all registered courses in the system """
    courses = Course.objects.all()
    context = {
        "courses": courses,
    }
    return render(request, 'course/course_list.html', context)


@login_required
@lecturer_required
def student_list(request):
    """ Show list of all registered students in the system """
    students = Student.objects.all()
    user_type = "Student"
    context = {
        "students": students,
        "user_type": user_type,
    }
    return render(request, 'students/student_list.html', context)


@login_required
@lecturer_required
def staff_list(request):
    """ Show list of all registered staff """
    staff = User.objects.filter(is_student=False)
    user_type = "Staff"
    context = {
        "staff": staff,
        "user_type": user_type,
    }
    return render(request, 'staff/staff_list.html', context)


@login_required
@lecturer_required
def session_list_view(request):
    """ Show list of all sessions """
    sessions = Session.objects.all().order_by('-session')
    return render(request, 'result/manage_session.html', {
        "sessions": sessions,
    })


@login_required
@lecturer_required
def session_add_view(request):
    """
    check request method, if POST we add session otherwise
    show empty form
    """
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Session added successfully ! ')

    else:
        form = SessionForm()
    return render(request, 'result/session_update.html', {'form': form})


@login_required
@lecturer_required
def session_update_view(request, pk):
    session = Session.objects.get(pk=pk)
    if request.method == 'POST':
        a = request.POST.get('is_current_session')
        if a == '2':
            unset = Session.objects.get(is_current_session=True)
            unset.is_current_session = False
            unset.save()
            form = SessionForm(request.POST, instance=session)
            if form.is_valid():
                form.save()
                messages.success(request, 'Session updated successfully ! ')
        else:
            form = SessionForm(request.POST, instance=session)
            if form.is_valid():
                form.save()
                messages.success(request, 'Session updated successfully ! ')

    else:
        form = SessionForm(instance=session)
    return render(request, 'result/session_update.html', {'form': form})


@login_required
@lecturer_required
def session_delete_view(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if session.is_current_session == True:
        messages.info(request, "You cannot delete current session")
        return redirect('manage_session')
    else:
        session.delete()
        messages.success(request, "Session successfully deleted")
    return redirect('manage_semester')


@login_required
@lecturer_required
def semester_list_view(request):
    semesters = Semester.objects.all().order_by('-session')
    return render(request, 'result/manage_semester.html', {
        "semesters": semesters,
    })


@login_required
@lecturer_required
def semester_add_view(request):
    if request.method == 'POST':
        form = SemesterForm(request.POST)
        if form.is_valid():
            # returns string of 'True' if the user selected Yes
            data = form.data.get('is_current_semester')
            if data == 'True':
                semester = form.data.get('semester')
                ss = form.data.get('session')
                session = Session.objects.get(pk=ss)
                try:
                    if Semester.objects.get(semester=semester, session=ss):
                        messages.info(
                            request, semester + " semester in " +
                            session.session + " session already exist")
                        return redirect('create_new_semester')
                except:
                    semester = Semester.objects.get(is_current_semester=True)
                    semester.is_current_semester = False
                    semester.save()
                    form.save()
            form.save()
            messages.success(request, 'Semester added successfully ! ')
            return redirect('manage_semester')
    else:
        form = SemesterForm()
    return render(request, 'result/semester_update.html', {'form': form})


@login_required
@lecturer_required
def semester_update_view(request, pk):
    semester = Semester.objects.get(pk=pk)
    if request.method == 'POST':
        # returns string of 'True' if the user selected yes for 'is current semester'
        if request.POST.get('is_current_semester') == 'True':
            unset_semester = Semester.objects.get(is_current_semester=True)
            unset_semester.is_current_semester = False
            unset_semester.save()
            unset_session = Session.objects.get(is_current_session=True)
            unset_session.is_current_session = False
            unset_session.save()
            new_session = request.POST.get('session')
            form = SemesterForm(request.POST, instance=semester)
            if form.is_valid():
                set_session = Session.objects.get(pk=new_session)
                set_session.is_current_session = True
                set_session.save()
                form.save()
                messages.success(request, 'Semester updated successfully !')
                return redirect('manage_semester')
        else:
            form = SemesterForm(request.POST, instance=semester)
            if form.is_valid():
                form.save()
                return redirect('manage_semester')

    else:
        form = SemesterForm(instance=semester)
    return render(request, 'result/semester_update.html', {'form': form})


@login_required
@lecturer_required
def semester_delete_view(request, pk):
    semester = get_object_or_404(Semester, pk=pk)
    if semester.is_current_semester == True:
        messages.info(request, "You cannot delete current semester")
        return redirect('manage_semester')
    else:
        semester.delete()
        messages.success(request, "Semester successfully deleted")
    return redirect('manage_semester')

@login_required
@admin_required
def StaffAddView(request):
    """A function that add lecturer details to the database from a CSV file"""
    template = "registration/add_staff.html"
    Users = get_user_model()
    prompt = {'order': 'Just upload the csv file for now'}
    if request.method == "GET":
        return render(request, template, prompt)
    csv_file = request.FILES['file']

    # is it really a csv file??
    if not csv_file.name.endswith('.csv'):
        messages.error(request, "This is not a CSV file")
    data_set = csv_file.read().decode('UTF-8')

    # setup a stream which is when we loop through each line,
    # and handle each student data in the stream.
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        raw_password = User.objects.make_random_password()
        hashed_password = make_password(raw_password)
        usernames = column[0][0].lower() + column[1].lower()
        _, lecturer_details = Users.objects.update_or_create(
            password=hashed_password,
            last_login="2020-08-03 09:46:42.521991",
            is_superuser="0",
            username=usernames,
            first_name=column[0],
            last_name=column[1],
            is_staff="0",
            is_active="1",
            date_joined="2020-08-03 09:46:42",
            is_student="0",
            is_lecturer="1",
            phone=column[2],
            address=column[3],
            picture=None,
            email=column[4])
        default_password_staff.delay(usernames, raw_password)
    context = {}
    return render(request, template, context)


@login_required
@lecturer_required
def edit_staff(request, pk):
    staff = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = StaffAddForm(request.POST, instance=staff)
        if form.is_valid():
            staff.save()
            return redirect('staff_list')
    else:
        form = StaffAddForm(instance=staff)
    return render(request, 'registration/edit_staff.html', {'form': form})


@login_required
@lecturer_required
def delete_staff(request, pk):
    staff = get_object_or_404(User, pk=pk)
    staff.delete()
    return redirect('staff_list')


@login_required
def StudentAddView(request):
    """A function that add users details to the database from a CSV file"""
    template = "registration/add_student.html"
    Users = get_user_model()
    prompt = {'order': 'Just upload the csv file for now'}

    if request.method == "GET":
        return render(request, template, prompt)

    csv_file = request.FILES['file']
    csv_file_w = csv_file

    if not csv_file.name.endswith('.csv'):
        HttpResponseRedirect(request, "This is not a CSV file")

    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    try:
        for column in csv.reader(io_string, delimiter=',', quotechar="|"):
            raw_password = User.objects.make_random_password()
            hashed_password = make_password(raw_password)
            usernames = column[0][0].lower() + column[1].lower()
            _, student_details = Users.objects.update_or_create(
                password=hashed_password,
                last_login="2020-08-03 09:46:42.521991",
                is_superuser="0",
                username=usernames,
                first_name=column[0],
                last_name=column[1],
                is_staff="0",
                is_active="1",
                date_joined="2020-08-03 09:46:42",
                is_student="1",
                is_lecturer="0",
                phone=column[2],
                address=column[3],
                picture=None,
                email=column[4])
            _, student_profile = Student.objects.update_or_create(
                user=User.objects.get(username=usernames),
                id_number=column[5],
                level=column[6],
                department=column[7],
                faculty=column[8])
            # lauch celery task
            default_password.delay(column[5 ], raw_password)
            # response = HttpResponse(csv_file_w, content_type='text/csv')
            # response['Content-Disposition'] = 'attachment; filename="student_details.csv"'
            # writer = csv.writer(response)
            # writer.writerow([column[0], raw_password])           
    except IndexError:
        """Other Possible Exceptions: IndexError, Integrity Error"""
        messages.error(request, "Index Error:  Your CSV files is incomplete")
    context = {}
    return render(request, template, context)

@login_required
@lecturer_required
def edit_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        form = StudentAddForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentAddForm(instance=student)
    return render(request, 'registration/edit_student.html', {'form': form})


@login_required
@lecturer_required
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.delete()
    return redirect('student_list')


@login_required
@admin_required
def CourseAddView(request):
    template = 'course/course_form.html'
    prompt = {'order': 'upload courses in csv format'}
    if request.method == "GET":
        return render(request, template, prompt)
    csv_file = request.FILES['file']

    if not csv_file.name.endswith('.csv'):
        HttpResponseRedirect(request, "You just uploaded a wrong file")

    data_set = csv_file.read().decode('UTF-8')

    io_string = io.StringIO(data_set)
    next(io_string)
    try:
        for column in csv.reader(io_string, delimiter=',', quotechar="|"):
            _, courses = Course.objects.update_or_create(
                courseTitle=column[0],
                courseCode=column[1],
                courseUnit=column[2],
                description=column[3],
                level=column[4],
                semester=column[5],
                is_elective=column[6]
            )
    except:
        messages.error(request, "Integrity Error:  course already exists")
    context = {}
    return render(request, template, context)


@login_required
@lecturer_required
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        form = CourseAddForm(request.POST, instance=course)
        if form.is_valid():
            course.save()
            messages.success(request, "Successfully Updated")
            return redirect('course_list')
    else:
        form = CourseAddForm(instance=course)
    return render(request, 'course/course_form.html', {'form': form})


@method_decorator([login_required, lecturer_required], name='dispatch')
class CourseAllocationView(CreateView):
    form_class = CourseAllocationForm
    template_name = 'course/course_allocation.html'

    def get_form_kwargs(self):
        kwargs = super(CourseAllocationView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # if a staff has been allocated a course before update it else create new
        lecturer = form.cleaned_data['lecturer']
        selected_courses = form.cleaned_data['courses']
        courses = ()
        for course in selected_courses:
            courses += (course.pk, )
        print(courses)

        try:
            a = CourseAllocation.objects.get(lecturer=lecturer)
        except:
            a = CourseAllocation.objects.create(lecturer=lecturer)
        for i in range(0, selected_courses.count()):
            a.courses.add(courses[i])
            a.save()
        return redirect('course_allocation_view')


@login_required
@admin_required
def course_allocation_upload(request):
    """[summary]
    """
    template = 'course/course_allocation_upload.html'
    prompt = {'order': 'upload courses_allocations in csv format'}
    if request.method == "GET":
        return render(request, template, prompt)

    csv_file = request.FILES['file']

    if not csv_file.name.endswith('.csv'):
        HttpResponseRedirect(request, "You just uploaded a wrong file")

    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        try:
            allocations = CourseAllocation.objects.get(
                lecturer=User.objects.get(username=column[0]))
        except:
            allocations = CourseAllocation.objects.create(
                lecturer=User.objects.get(username=column[0]))
        allocations.courses.add(Course.objects.get(courseCode=column[1]))
        allocations.save()
    context = {}
    return render(request, template, context)


@login_required
@lecturer_required
def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    course.delete()
    messages.success(request, 'Deleted successfully!')
    return redirect('course_list')


@login_required
@lecturer_required
def course_allocation_view(request):
    allocated_courses = CourseAllocation.objects.all()
    return render(request, 'course/course_allocation_view.html',
                  {"allocated_courses": allocated_courses})


@login_required
@lecturer_required
def withheld_course(request, pk):
    course = CourseAllocation.objects.get(pk=pk)
    course.delete()
    messages.success(request, 'successfully deallocated!')
    return redirect("course_allocation_view")


@login_required
def carry_over(request):
    if request.method == "POST":
        value = ()
        data = request.POST.copy()
        data.pop('csrfmiddlewaretoken', None)  # remove csrf_token
        for val in data.values():
            value += (val, )
        course = value[0]
        session = value[1]
        courses = CarryOverStudent.objects.filter(course__courseCode=course,
                                                  session=session)
        all_courses = Course.objects.all()
        sessions = Session.objects.all()
        signal_template = True
        context = {
            "all_courses": all_courses,
            "courses": courses,
            "signal_template": signal_template,
            "sessions": sessions
        }
        return render(request, 'course/carry_over.html', context)
    else:
        all_courses = Course.objects.all()
        sessions = Session.objects.all()
        return render(request, 'course/carry_over.html', {
            "all_courses": all_courses,
            "sessions": sessions
        })


@login_required
def repeat_list(request):
    students = RepeatingStudent.objects.all()
    return render(request, 'students/repeaters.html', {"students": students})


@login_required
def first_class_list(request):
    students = Result.objects.filter(cgpa__gte=4.5)
    return render(request, 'students/first_class_students.html',
                  {"students": students})

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
        current_semester = Semester.objects.get(is_current_semester=True)
        student = Student.objects.get(user__pk=request.user.id)
        taken_courses = TakenCourse.objects.filter(
            student__user__id=request.user.id, course__semester=current_semester)
        t = ()
        for i in taken_courses:
            t += (i.course.pk, )
        courses = Course.objects.filter(level=student.level, semester=current_semester).exclude(id__in=t)
        all_courses = Course.objects.filter(level=student.level, semester=current_semester)

        no_course_is_registered = False  # Check if no course is registered
        all_courses_are_registered = False

        registered_courses = Course.objects.filter(level=student.level, semester=current_semester).filter(
            id__in=t)
        if registered_courses.count(
        ) == 0:  # Check if number of registered courses is 0
            no_course_is_registered = True

        if registered_courses.count() == all_courses.count():
            all_courses_are_registered = True

        # total_semester_unit = 0
        # total_sec_semester_unit = 0
        total_registered_unit = 0
        # for i in courses:
        #     total_semester_unit += int(i.courseUnit)
        for i in registered_courses:
            total_registered_unit += int(i.courseUnit)
        context = {
            "all_courses_are_registered": all_courses_are_registered,
            "no_course_is_registered": no_course_is_registered,
            "current_semester": current_semester,
            "courses": courses,
            # "total_first_semester_unit": total_semester_unit,
            # "total_sec_semester_unit": total_sec_semester_unit,
            "registered_courses": registered_courses,
            "total_registered_unit": total_registered_unit,
            "student": student,
        }
        return render(request, 'course/course_registration.html', context)


@login_required
@student_required
def registered_courses(request):
    level = Student.objects.get(user__pk=request.user.id)
    courses = TakenCourse.objects.filter(student__user__id=request.user.id,
                                             course__level=level.level)
    context = {
        'courses': courses,
        'level': level,
        }
    return render(request, 'course/registered_courses.html', context)

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
                                         course__level=student.level,
                                         course__semester=current_semester
                                         )
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
    """View to handle WeasyPrint PDF for student Course Registration"""
    current_semester = Semester.objects.get(is_current_semester=True)
    current_session = Session.objects.get(is_current_session=True)
    student = Student.objects.get(user__pk=request.user.id)
    taken_courses = TakenCourse.objects.filter(
        student__user__id=request.user.id, course__semester=current_semester)
    t = ()
    for i in taken_courses:
        t += (i.course.pk, )
        registered_courses = Course.objects.filter(level=student.level, semester=current_semester).filter(
            id__in=t)
        total_registered_unit = 0
        for i in registered_courses:
            total_registered_unit += int(i.courseUnit)
    html = render_to_string(
        'course/pdf.html', {
            "student": student,
            "registered_courses": registered_courses,
            "total_registered_unit": total_registered_unit,
            "current_session": current_session,
            "current_semester": current_semester
        })
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = f'filname=student_{student.id_number}.pdf'
    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
        response,
        stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + '/css/pdf.css')])
    return response

@login_required
@student_required
def result_pdf(request):
    """View that allows student to print their result"""
    student = Student.objects.get(user__pk=request.user.id)
    current_semester = Semester.objects.get(is_current_semester=True)
    current_session = Session.objects.get(is_current_session=True)
    courses = TakenCourse.objects.filter(student__user__pk=request.user.id,
                                         course__level=student.level,
                                         course__semester=current_semester
                                       )
    result = Result.objects.filter(student__user__pk=request.user.id, semester=current_semester)
    current_CGPA = 0
    try:
        a = Result.objects.get(student__user__pk=request.user.id,
                               level=student.level,
                               semester="Second")
        current_CGPA = a.cgpa
    except:
        current_CGPA = 0

    point = 0
    cp = 0
    # cps = 0
    t = ()
    for i in courses:
        t += (i.course.pk, )
        registered_courses = Course.objects.filter(level=student.level).filter(
            id__in=t)
        total_registered_unit = 0
        for i in registered_courses:
            total_registered_unit += int(i.courseUnit)
    html = render_to_string(
        'result/resultpdf.html', {
            "student": student,
            "courses": courses,
            "result": result,
            "current_CGPA": current_CGPA,
            "registered_courses": registered_courses,
            "total_registered_unit": total_registered_unit,
            "current_semester": current_semester,
            "current_session": current_session,
            # "point": point,
            # "cp": cp
        })
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = f'filname=student_{student.id_number}.pdf'
    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
        response,
        stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + '/css/resultpdf.css')])
    return response

@login_required
@lecturer_required
def add_score(request):
    """
    Shows a page where a lecturer will select a course allocated to him for
    score entry in a specific semester and session.
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
    """
    Shows a page where a lecturer will add score for students that are taking courses allocated to him
    in a specific semester and session.
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


@login_required
@lecturer_required
def scoresheet_download(request):
    """A function that handles scoresheet template download for lecturers"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="scoresheet.csv"'
    writer = csv.writer(response)
    writer.writerow(['Matric No', 'CA', 'Exam'])
    return response
