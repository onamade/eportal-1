from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('profile/', views.profile, name='profile'),
    path('profile/view/<int:id>/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.profile_update, name='edit_profile'),
    path('password/', views.change_password, name='change_password'),
    path('result/print/<int:id>/',
         views.result_sheet_pdf_view,
         name='result_sheet_pdf_view'),
    path('', include('django.contrib.auth.urls')),
]
