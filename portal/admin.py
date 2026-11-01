from django.contrib import admin
from .models import AcademicConfiguration, SchoolClass, Subject, TeacherAssignment, Student, Grade

# Register your models here.
admin.site.register(AcademicConfiguration)
admin.site.register(SchoolClass)
admin.site.register(Subject)
admin.site.register(TeacherAssignment)
admin.site.register(Student)
admin.site.register(Grade)