from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Class, Subject
from .forms import ClassForm, SubjectForm

def academic_setup(request):
    if request.method == 'POST':
        if 'set_term' in request.POST:
            # Logic to set the active term
            term = request.POST.get('term')
            # Update the configuration with the new term
            # config.current_term = term
            # config.save()
            return redirect('academic_setup')

        elif 'add_class' in request.POST:
            form = ClassForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('academic_setup')

        elif 'delete_class' in request.POST:
            class_id = request.POST.get('class_id')
            Class.objects.filter(id=class_id).delete()
            return redirect('academic_setup')

        elif 'add_subject' in request.POST:
            form = SubjectForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('academic_setup')

        elif 'delete_subject' in request.POST:
            subject_id = request.POST.get('subject_id')
            Subject.objects.filter(id=subject_id).delete()
            return redirect('academic_setup')

    classes = Class.objects.all()
    subjects = Subject.objects.all()
    return render(request, 'portal/academic_setup.html', {'classes': classes, 'subjects': subjects})