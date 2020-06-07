from django.contrib import admin
from .models import TakenCourse, Result

# Register your models here.
class ScoreAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'ca',
                    'exam', 'total', 'grade', 'comment']


class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'gpa', 'semester', 'level', 'cgpa']


admin.site.register(TakenCourse, ScoreAdmin)
admin.site.register(Result, ResultAdmin)
