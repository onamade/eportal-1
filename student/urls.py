from django.urls import path
from . import views

urlpatterns = [
    path('result/', views.view_result, name="view_results"),
    path('course/registration/',
         views.course_registration,
         name='course_registration'),
    path('course/drop/', views.course_drop, name='course_drop'),
    path('coursepdf/',
         views.course_registration_pdf,
         name='course_registration_pdf'),
]
