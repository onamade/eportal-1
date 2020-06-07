from django.contrib import admin
from .models import Student, CarryOverStudent, RepeatingStudent

# Register your models here.
admin.site.register(Student)
admin.site.register(CarryOverStudent)
admin.site.register(RepeatingStudent)
