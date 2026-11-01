from django import forms
from .models import Student, TeacherAssignment, SchoolClass, Subject, AcademicConfiguration
from django.contrib.auth.models import User

# NEW TEACHER CREATION FORM
class TeacherCreationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        label="Password"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Hash the password properly
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
        return user

#NEW ACADEMIC TERM CREATION
class TeacherAssignmentForm(forms.ModelForm):
    class Meta:
        model = TeacherAssignment
        fields = ['teacher', 'school_class', 'subject']
        widgets = {
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'school_class': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = User.objects.filter(is_superuser=False)

    def clean(self):
        cleaned_data = super().clean()
        school_class = cleaned_data.get('school_class')
        subject = cleaned_data.get('subject')

        if school_class and subject:
            existing_assignment = TeacherAssignment.objects.filter(
                school_class=school_class, 
                subject=subject
            ).first()

            if existing_assignment:
                teacher_name = existing_assignment.teacher.get_full_name() or existing_assignment.teacher.username
                raise forms.ValidationError(
                    f"Already assigned! '{subject.subject_name}' in {school_class.class_name} "
                    f"is already assigned to {teacher_name}."
                )
        return cleaned_data



class StudentForm(forms.ModelForm):
    school_class = forms.ModelChoiceField(
        queryset = SchoolClass.objects.all(),
        empty_label = "Select Class",
        widget = forms.Select(attrs={'class':'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )
    class Meta:
        model = Student
        fields = ['admission_no', 'first_name', 'last_name', 'school_class']
        widgets = {
            'admission_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., ADM-101'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'school_class': forms.Select(attrs={'class': 'form-control'}),
        }


class TeacherAssignmentForm(forms.ModelForm):
    class Meta:
        model = TeacherAssignment
        fields = ['teacher', 'school_class', 'subject']
        widgets = {
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'school_class': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = User.objects.filter(is_superuser=False)

    def clean(self):
        cleaned_data = super().clean()
        school_class = cleaned_data.get('school_class')
        subject = cleaned_data.get('subject')

        if school_class and subject:
            existing_assignment = TeacherAssignment.objects.filter(
                school_class=school_class, 
                subject=subject
            ).first()

            if existing_assignment:
                teacher_name = existing_assignment.teacher.get_full_name() or existing_assignment.teacher.username
                raise forms.ValidationError(
                    f"Already assigned! '{subject.subject_name}' in {school_class.class_name} "
                    f"is already assigned to {teacher_name}."
                )
        return cleaned_data

class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ['class_name']
        widgets = {
            'class_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Form 1'}),
        }

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['subject_name']
        widgets = {
            'subject_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Mathematics, Physics'}),
        }

class AcademicTermForm(forms.Form):
    term = forms.ChoiceField(
        choices=AcademicConfiguration.TERM_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
