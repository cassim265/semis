from django.db import models

class Class(models.Model):
    class_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.class_name

class Subject(models.Model):
    subject_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.subject_name

class AcademicTerm(models.Model):
    term_number = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return f'Term {self.term_number}'