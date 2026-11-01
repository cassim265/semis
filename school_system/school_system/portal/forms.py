from django import forms
from .models import Class, Subject

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['class_name']
        widgets = {
            'class_name': forms.TextInput(attrs={'placeholder': 'e.g. Form 1', 'class': 'form-control'}),
        }

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['subject_name']
        widgets = {
            'subject_name': forms.TextInput(attrs={'placeholder': 'e.g. Mathematics, Physics', 'class': 'form-control'}),
        }