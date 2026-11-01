from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('login/', views.custom_login, name='login'),
    path('logout', views.custom_logout, name='logout'),
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('grade_entry/<int:class_id>/<int:subject_id>/', views.grade_entry, name='grade_entry'),
    path('admin_matrix/', views.admin_matrix, name='admin_matrix'),

    path('add_student/', views.add_student, name='add_student'),
    path('assign_teacher/', views.assign_teacher, name='assign_teacher'),
    path('teacher/academic_setup', views.academic_setup, name='academic_setup'),
    path('student/<int:student_id>/student_report_card/', views.student_report_card, name='student_report_card'),
    path('admin/promote_students', views.promote_academic_year, name='promote_students')
]