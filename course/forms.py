from django import forms
from .models import Course
from student.models import LEVEL
from calendar.models import SEMESTER
from users.models import User
from course.models import CourseAllocation


class CourseAddForm(forms.ModelForm):
    courseTitle = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
        }),
        label="*Course Title",
    )
    courseCode = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
        }),
        label="*Course Code",
    )

    courseUnit = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
        }),
        label="*Course Unit",
    )

    description = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
        }),
        label="Add a little description",
        required=False,
    )

    level = forms.CharField(
        widget=forms.Select(choices=LEVEL,
                            attrs={
                                'class': 'browser-default custom-select',
                            }),
        label="*Level",
    )

    semester = forms.CharField(
        max_length=30,
        widget=forms.Select(choices=SEMESTER,
                            attrs={
                                'class': 'form-control',
                            }),
        label="*Semester",
    )

    is_elective = forms.BooleanField(label="*is_elective", required=False)

    class Meta:
        model = Course
        fields = [
            'courseCode', 'courseTitle', 'courseUnit', 'level', 'description',
            'semester', 'is_elective'
        ]


class CourseAllocationForm(forms.ModelForm):
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all().order_by('level'),
        widget=forms.CheckboxSelectMultiple,
        required=True)
    lecturer = forms.ModelChoiceField(
        queryset=User.objects.filter(is_lecturer=True),
        widget=forms.Select(attrs={'class': 'browser-default custom-select'}),
        label="lecturer",
    )

    class Meta:
        model = CourseAllocation
        fields = ['lecturer', 'courses']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(CourseAllocationForm, self).__init__(*args, **kwargs)
        self.fields['lecturer'].queryset = User.objects.filter(
            is_lecturer=True)
