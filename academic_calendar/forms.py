from django import forms

from .models import Session, SEMESTER, Semester

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['session']


class SemesterForm(forms.ModelForm):
    semester = forms.CharField(
        widget=forms.Select(choices=SEMESTER,
                            attrs={
                                'class': 'browser-default custom-select',
                            }),
        label="semester",
    )
    is_current_semester = forms.CharField(
        widget=forms.Select(choices=((True, 'Yes'), (False, 'No')),
                            attrs={
                                'class': 'browser-default custom-select',
                            }),
        label="is current semester ?",
    )
    session = forms.ModelChoiceField(
        queryset=Session.objects.all(),
        widget=forms.Select(attrs={
            'class': 'browser-default custom-select',
        }),
        required=True)

    next_semester_begins = forms.DateTimeField(
        widget=forms.TextInput(attrs={
            'type': 'date',
        }), required=True)

    class Meta:
        model = Semester
        fields = [
            'semester', 'is_current_semester', 'session',
            'next_semester_begins'
        ]