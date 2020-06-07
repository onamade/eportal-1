from django.contrib import admin
from .models import CourseAllocation, Course


# Register your models here.
class AllocationAdmin(admin.ModelAdmin):
    list_display = ['lecturer', ]

admin.site.register(CourseAllocation, AllocationAdmin)
admin.site.register(Course)
