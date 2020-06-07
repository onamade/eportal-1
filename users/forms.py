from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms import BaseModelFormSet

from .models import User
from student.models import LEVEL, Student
from result.models import TakenCourse



class StaffAddForm(UserCreationForm):
    address = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'type': 'text',
            'class': 'form-control',
        }),
        label="Address",
    )

    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'type': 'text',
            'class': 'form-control',
        }),
        label="Mobile No.",
    )

    firstname = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'type': 'text',
            'class': 'form-control',
        }),
        label="Firstname",
    )

    lastname = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'type': 'text',
            'class': 'form-control',
        }),
        label="Lastname",
    )

    email = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'type': 'text',
            'class': 'form-control',
        }),
        label="Email",
    )

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic()
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_lecturer = True
        user.first_name = self.cleaned_data.get('firstname')
        user.last_name = self.cleaned_data.get('lastname')
        user.phone = self.cleaned_data.get('phone')
        user.address = self.cleaned_data.get('address')
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
        return user


class StudentAddForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'type': 'text',
            'class': 'form-control',
        }),
        label="Username",
    )
    address = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'type': 'text',
            'class': 'form-control',
        }),
        label="Address",
    )

    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'type': 'text',
            'class': 'form-control',
        }),
        label="Mobile No.",
    )

    firstname = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'type': 'text',
            'class': 'form-control',
        }),
        label="Firstname",
    )

    lastname = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'type': 'text',
            'class': 'form-control',
        }),
        label="Lastname",
    )

    level = forms.CharField(widget=forms.Select(
        choices=LEVEL, attrs={
            'class': 'browser-default custom-select',
        }), )

    email = forms.EmailField(
        widget=forms.TextInput(attrs={
            'type': 'email',
            'class': 'form-control',
        }),
        label="Email Address",
    )

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic()
    def save(self):
        user = super().save(commit=False)
        user.is_student = True
        user.first_name = self.cleaned_data.get('firstname')
        user.last_name = self.cleaned_data.get('lastname')
        user.phone = self.cleaned_data.get('phone')
        user.email = self.cleaned_data.get('email')
        user.save()
        student = Student.objects.create(user=user,
                                         id_number=user.username,
                                         level=self.cleaned_data.get('level'))
        student.save()
        return user

class ChangePasswordForm(forms.ModelForm):
    id = forms.CharField(widget=forms.HiddenInput())
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Old password",
        required=True)

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="New password",
        required=True)
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm new password",
        required=True)

    class Meta:
        model = User
        fields = ['id', 'password', 'password1', 'password2']

    def clean(self):
        super(ChangePasswordForm, self).clean()
        password = self.cleaned_data.get('password')
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        id = self.cleaned_data.get('id')
        user = User.objects.get(pk=id)
        if not user.check_password(password):
            self._errors['password'] = self.error_class(
                ['Old password don\'t match'])
        if password1 and password1 != password2:
            self._errors['password1'] = self.error_class(
                ['Passwords don\'t match'])
        return self.cleaned_data


class CourseRegitsrationForm(forms.ModelForm):
    class Meta:
        model = TakenCourse
        fields = ('course', )
        widgets = {'course': forms.CheckboxSelectMultiple}


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Firstname",
        max_length=30,
        required=False)
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Lastname",
        max_length=30,
        required=False)
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label="Email",
        max_length=75,
        required=False)
    phone = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Phone Number",
        max_length=16,
        required=False)

    address = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Home Address",
        max_length=200,
        required=False)

    picture = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        label="Upload picture",
        required=False)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'address', 'picture'
        ]
