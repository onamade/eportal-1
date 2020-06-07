from django.urls import path
from . import views

urlpatterns = [
    path('score/', views.add_score, name='add_score'),
    path('score/<int:id>/', views.add_score_for, name='add_score_for'),
]
