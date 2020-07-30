from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views
from .settings import base
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# from result import views as result_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('django.contrib.auth.urls')),
    path('', include('users.urls')),
    path('', include('administrator.urls')),
    path('', include('result.urls')),
    path('', include('lecturer.urls')),
    path('', include('student.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('accounts/logout/', views.LogoutView.as_view(), name='logout', kwargs={'next_page': '/'}),
    # path('register/student/', result_view.StudentAddView.as_view(), name='student_signup'),
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(base.MEDIA_URL, document_root=base.MEDIA_ROOT)
urlpatterns += static(base.STATIC_URL, document_root=base.STATIC_ROOT)
