from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class AcademicConfiguration(models.Model):
    TERM_CHOICES = [
        (1, 'Term 1'),
        (2, 'Term 2'),
        (3, 'Term 3'),
    ]
    current_term = models.IntegerField(choices=TERM_CHOICES)
    academic_year = models.CharField(max_length=9, default='2025/2026')
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"Term{self.current_term}({self.academic_year})"



class SchoolClass(models.Model):
    class_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.class_name

class Subject(models.Model):
    subject_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.subject_name

class TeacherAssignment(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    class Meta:
        #prevent duplicate active assignment for the same class and subject
        unique_together = ('school_class', 'subject')

    def __str__(self):
        return f"{self.teacher.username} - {self.subject.subject_name}({self.school_class.class_name})"

#NEW MODEL FOR ARCHIVED ASSIGNMENTS
class PreviousAssignment(models.Model):
    teacher_name = models.CharField(max_length=150)
    class_name = models.CharField(max_length=100)
    subject_name = models.CharField(max_length=100)
    academic_year = models.CharField(max_length=50)
    archived_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.teacher_name} - {self.subject_name}({self.class_name})[{self.academic_year}]"

class Student(models.Model):
    admission_no = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.SET_NULL, null=True)
    is_graduated = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name}{self.last_name}({self.admission_no})"

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    term = models.IntegerField()
    academic_year = models.CharField(max_length=9)
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    is_authorized = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.first_name} = {self.subject.subject_name}: {self.marks}"
