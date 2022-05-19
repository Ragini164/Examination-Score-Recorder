from django.urls import re_path
from . import views
urlpatterns = [
    
    re_path(r'^student_dashboard/$', views.student_dashboard, name='student_dashboard'),
    re_path(r'^student_exams/$', views.student_exams, name='student_exams'),
    re_path(r'^student_attempt_exam/$', views.student_attempt_exam, name='student_attempt_exam'),
    re_path(r'^student_approved_exams/$', views.student_approved_exams, name='student_approved_exams'),
    re_path(r'^student_verify/', views.student_verify, name='student_verify'),
    re_path(r'^student_progress/$', views.faculty_register_evaluate, name='student_progress'),
    re_path(r'^student_answer_key/$', views.student_answer_key, name='student_answer_key'),
    re_path(r'^$', views.login, name='login'),
    re_path(r'^signup/$', views.signup, name='signup'),
    re_path(r'^sign_out/$', views.sign_out, name='sign_out'),
    re_path(r'^authenticate/(?P<token>[A-Za-z0-9_\.-]*)/$', views.authenticate, name='authenticate'),
    re_path(r'^get_exams_by_course/$', views.get_exams_by_course, name='get_exams_by_course'),
    
]
