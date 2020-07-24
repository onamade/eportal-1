import csv
import io

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils.decorators import method_decorator
from django.views.generic import CreateView

from result.models import TakenCourse, Result
from users.decorators import lecturer_required, admin_required
from student.models import Student, CarryOverStudent, RepeatingStudent
from course.models import Course, CourseAllocation
from users.models import User
from users.forms import StaffAddForm, StudentAddForm
from academic_calendar.models import Session, Semester
from academic_calendar.forms import SessionForm, SemesterForm
from course.forms import CourseAddForm, CourseAllocationForm

from .tasks import default_password, default_password_staff


# Create your views here.
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
    """ check request method, if POST we add session otherwise show empty form """
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
    semesters = Semester.objects.all().order_by('-semester')
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


# @method_decorator([login_required, lecturer_required], name='dispatch')
@login_required
@admin_required
def StaffAddView(request):
    """A function that add lecturer details to the database from a CSV file

    Args:
        request ([type]): [description]
    """
    template = "registration/add_staff.html"
    Users = get_user_model()

    # setup a stream which is when we loop through each line we are
    # to handle a data in a stream
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
        _, lecturer_details = Users.objects.update_or_create(
            password=hashed_password,
            last_login="2020-06-07 06:46:42.521991",
            is_superuser="0",
            username=column[1],
            first_name=column[2],
            last_name=column[3],
            is_staff="0",
            is_active="1",
            date_joined="2020-06-07 06:46:42",
            is_student="0",
            is_lecturer="1",
            phone=column[4],
            address=column[5],
            picture=None,
            email=column[6])
        default_password_staff.delay(column[1], raw_password)
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
    """A function that add users details to the database from a CSV file

    Args:
        request ([type]): [description]
    """
    template = "registration/add_student.html"
    Users = get_user_model()

    # setup a stream which is when we loop through each line we are
    # to handle a data in a stream
    prompt = {'order': 'Just upload the csv file for now'}
    if request.method == "GET":
        return render(request, template, prompt)
    csv_file = request.FILES['file']

    # is it really a csv file??
    if not csv_file.name.endswith('.csv'):
        HttpResponseRedirect(request, "This is not a CSV file")

    data_set = csv_file.read().decode('UTF-8')
    # setup a stream which is when we loop through each line,
    # and handle each student data in the stream.
    io_string = io.StringIO(data_set)
    next(io_string)
    try:
        for column in csv.reader(io_string, delimiter=',', quotechar="|"):
            # make_password(column[0]),
            raw_password = User.objects.make_random_password()
            hashed_password = make_password(raw_password)
            _, student_details = Users.objects.update_or_create(
                password=hashed_password,
                last_login="2020-06-08 09:46:42.521991",
                is_superuser="0",
                username=column[1],
                first_name=column[2],
                last_name=column[3],
                is_staff="0",
                is_active="1",
                date_joined="2020-06-08 09:46:42",
                is_student="1",
                is_lecturer="0",
                phone=column[4],
                address=column[5],
                picture=None,
                email=column[6])
            _, student_profile = Student.objects.update_or_create(
                user=User.objects.get(username=column[1]),
                id_number=column[7],
                level=column[8],
                faculty=column[9],
                department=column[10])
                # lauch asynchronous task
            # response = HttpResponse(content_type='text/csv')
            # response['Content-Disposition'] = 'attachment; filename="student_deatails.csv"'
            # writer = csv.writer(response)
            # writer.writerow([column[7], raw_password])
            default_password.delay(column[7], raw_password)
    except IndexError:
        """Possible Exceptions: IndexError, Integrity Error
        """
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
