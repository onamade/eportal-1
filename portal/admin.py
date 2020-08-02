from django.contrib import admin


from .models import (
    User, Student, CarryOverStudent, RepeatingStudent, Course,
    TakenCourse, Result, Semester, CourseAllocation, Session
)

admin.site.register(User)

admin.site.register(Session)
admin.site.register(Semester)

admin.site.register(Student)
admin.site.register(CarryOverStudent)
admin.site.register(RepeatingStudent)

class AllocationAdmin(admin.ModelAdmin):
    list_display = ['lecturer', ]

admin.site.register(CourseAllocation, AllocationAdmin)
admin.site.register(Course)

class ScoreAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'ca',
                    'exam', 'total', 'grade', 'comment']


class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'gpa', 'semester', 'level', 'cgpa']


admin.site.register(TakenCourse, ScoreAdmin)
admin.site.register(Result, ResultAdmin)