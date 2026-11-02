from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import TeacherAssignment, SchoolClass, Subject, Student, Grade, AcademicConfiguration, PreviousAssignment
from .forms import StudentForm, TeacherAssignmentForm, TeacherCreationForm, AcademicTermForm, SubjectForm, SchoolClassForm
from django.db.models import Q, Sum
import datetime
from .utils import calculate_grade


# 1. SMART LOGIN VIEW
def custom_login(request):
    # If already logged in, route immediately based on role
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_matrix')
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Decide flow based on user type upon login
            if user.is_superuser:
                return redirect('admin_matrix')
            else:
                return redirect('teacher_dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'portal/login.html', {'form': form})

def custom_logout(request):
    logout(request)
    messages.info(request, "You have been logged out successifully")
    return redirect('login')


# 2. TEACHER DASHBOARD (Teacher Access Only)
@login_required(login_url='login')
def teacher_dashboard(request):
    # Block superusers from teacher dashboard if desired, or let them view it
    assignments = TeacherAssignment.objects.filter(teacher=request.user)
    assigned_classes = SchoolClass.objects.filter(
        id__in=assignments.values_list('school_class_id', flat=True)
    ).distinct()

    selected_class_id = request.GET.get('class_id')
    selected_subject_id = request.GET.get('subject_id')

    selected_class = None
    selected_subject = None
    available_subjects = []
    students = []
    config = AcademicConfiguration.objects.first()

    if selected_class_id:
        selected_class = get_object_or_404(SchoolClass, id=selected_class_id)
        available_subjects = Subject.objects.filter(
            id__in=assignments.filter(school_class=selected_class).values_list('subject_id', flat=True)
        )

        if selected_subject_id:
            selected_subject = get_object_or_404(Subject, id=selected_subject_id)
            students = Student.objects.filter(school_class=selected_class)

            if config:
                grades = Grade.objects.filter(
                    subject=selected_subject,
                    term=config.current_term,
                    academic_year=config.academic_year,
                    student__school_class=selected_class
                )
                grade_map = {g.student_id: (g.marks, g.is_authorized) for g in grades}

                for student in students:
                    info = grade_map.get(student.id, ('-', False))
                    student.current_grade = info[0]
                    student.is_locked = info[1]

    context = {
        'assigned_classes': assigned_classes,
        'selected_class': selected_class,
        'available_subjects': available_subjects,
        'selected_subject': selected_subject,
        'students': students,
        'config': config
    }
    return render(request, 'portal/teacher_dashboard.html', context)


# 3. DEDICATED GRADE ENTRY PAGE
@login_required(login_url='login')
def grade_entry(request, class_id, subject_id):
    school_class = get_object_or_404(SchoolClass, id=class_id)
    subject = get_object_or_404(Subject, id=subject_id)
    student_id = request.GET.get('student_id')
    
    config = AcademicConfiguration.objects.first()

    if student_id:
        students = Student.objects.filter(id=student_id, school_class=school_class)
    else:
        students = Student.objects.filter(school_class=school_class)

    if request.method == "POST":
        for student in students:
            raw_marks = request.POST.get(f"grade_for_student_{student.id}", "").strip()
            if raw_marks != "":
                try:
                    marks_val = float(raw_marks)
                    if 0 <= marks_val <= 100:
                        Grade.objects.update_or_create(
                            student=student,
                            subject=subject,
                            term=config.current_term if config else 1,
                            academic_year=config.academic_year if config else '',
                            defaults={'marks': marks_val}
                        )
                except ValueError:
                    pass

        messages.success(request, "Grades updated successfully!")
        return redirect(f"/teacher/grade_entry/{class_id}/{subject_id}/?student_id={student_id}" if student_id else f"/teacher/grade_entry/{class_id}/{subject_id}/")

    # Clear old messages on GET requests so stale login/logout alerts don't stack up
    storage = messages.get_messages(request)
    storage.used = True

    if config:
        grades = Grade.objects.filter(
            subject=subject,
            term=config.current_term,
            academic_year=config.academic_year,
            student__in=students
        )
        grade_map = {g.student_id: (g.marks, g.is_authorized) for g in grades}

        for student in students:
            info = grade_map.get(student.id, ('', False))
            student.current_grade = info[0]
            student.is_locked = info[1]

    context = {
        'school_class': school_class,
        'subject': subject,
        'students': students,
        'config': config
    }
    return render(request, 'portal/grade_entry.html', context)


# 4. ADMIN MATRIX VIEW (SUPERUSER ONLY)
@user_passes_test(lambda u: u.is_authenticated and u.is_superuser, login_url='login')
def admin_matrix(request):
    # 1. Top KPI Summary Stats
    total_students = Student.objects.count()
    total_teachers = TeacherAssignment.objects.values('teacher_id').distinct().count()
    total_subjects = Subject.objects.count()
    active_config = AcademicConfiguration.objects.filter(is_active=True).first() or AcademicConfiguration.objects.first()

    # 2. Class Selection for Matrix
    classes = SchoolClass.objects.all()
    selected_class_id = request.GET.get('class_id')

    selected_class = None
    if selected_class_id:
        selected_class = SchoolClass.objects.filter(id=selected_class_id).first()
    if not selected_class and classes.exists():
        selected_class = classes.first()

    # 3. Construct Grades Matrix for Selected Class
    all_subjects = list(Subject.objects.all())
    student_matrix = []

    if selected_class:
        students = Student.objects.filter(school_class=selected_class).order_by('first_name')
        
        # Pre-fetch all grades for selected class students to avoid N+1 queries
        grades = Grade.objects.filter(
            student__school_class=selected_class,
            term=active_config.current_term if active_config else 1
        ).select_related('student', 'subject')

        # Build lookup map: (student_id, subject_id) -> score
        grade_map = {(g.student_id, g.subject_id): g.marks for g in grades}

        for student in students:
            subject_scores = []
            for subj in all_subjects:
                score = grade_map.get((student.id, subj.id), '-')
                subject_scores.append({'subject_id': subj.id, 'score': score})
            
            student_matrix.append({
                'student': student,
                'scores': subject_scores
            })
    # 4. Teacher Grade Submission Status
    assignments = TeacherAssignment.objects.select_related('teacher', 'subject', 'school_class').all()

    # Get set of (subject_id, class_id) or subject_ids where grades exist for the active term
    submitted_grades = Grade.objects.filter(
        term=active_config.current_term if active_config else 1
    ).values_list('subject_id', 'student__school_class_id').distinct()

    submitted_pairs = set(submitted_grades)  # set of (subject_id, school_class_id) tuples

    teacher_submission_status = []
    for assign in assignments:
        # Check if any grades exist for this assigned subject & class
        has_submitted = (assign.subject_id, assign.school_class_id) in submitted_pairs if hasattr(assign, 'school_class_id') else Grade.objects.filter(subject_id=assign.subject_id).exists()
        
        teacher_submission_status.append({
            'teacher_name': assign.teacher.get_full_name() or assign.teacher.username,
            'subject_name': assign.subject.subject_name,
            'class_name': assign.school_class.class_name if hasattr(assign, 'school_class') and assign.school_class else "All Classes",
            'is_submitted': has_submitted,
        })

    

    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_subjects': total_subjects,
        'active_config': active_config,
        'classes': classes,
        'selected_class': selected_class,
        'all_subjects': all_subjects,
        'student_matrix': student_matrix,
        'teacher_submission_status':teacher_submission_status
    }
    return render(request, 'portal/admin_matrix.html', context)



# ADD STUDENT VIEW (WITH TABLE & SEARCH)
@user_passes_test(lambda u: u.is_authenticated and u.is_superuser, login_url='login')
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_student')
    else:
        form = StudentForm()

    # Get selected class ID from search/filter bar
    selected_class_id = request.GET.get('class_id')
    search_query = request.GET.get('search', '')

    students = Student.objects.all()

    # Filter by class if selected
    if selected_class_id:
        students = students.filter(school_class_id=selected_class_id)

    # Filter by search term if provided
    if search_query:
        students = students.filter(
            first_name__icontains=search_query
        ) | students.filter(
            last_name__icontains=search_query
        ) | students.filter(
            admission_no__icontains=search_query
        )

    classes = SchoolClass.objects.all()

    context = {
        'form': form,
        'students': students,
        'classes': classes,
        'selected_class_id': selected_class_id,
        'search_query': search_query,
    }
    return render(request, 'portal/add_student.html', context)


# 2. TEACHER ASSIGNMENT VIEW
@user_passes_test(lambda u: u.is_authenticated and u.is_superuser, login_url='login')
def assign_teacher(request):
    assignments = TeacherAssignment.objects.select_related('teacher', 'school_class', 'subject').all()
    previous_assignments = PreviousAssignment.objects.all().order_by('-archived_at')

    teacher_form = TeacherCreationForm()
    assignment_form = TeacherAssignmentForm()

    if request.method == 'POST':
        # 1. CREATE TEACHER ACCOUNT
        if 'create_teacher' in request.POST:
            teacher_form = TeacherCreationForm(request.POST)
            if teacher_form.is_valid():
                user = teacher_form.save()
                messages.success(request, f"Teacher account '{user.username}' created successfully!")
                return redirect('assign_teacher')

        # 2. ASSIGN TEACHER TO SUBJECT
        elif 'assign_subject' in request.POST:
            assignment_form = TeacherAssignmentForm(request.POST)
            if assignment_form.is_valid():
                assignment = assignment_form.save()
                messages.success(
                    request, 
                    f"Successfully assigned {assignment.teacher.get_full_name() or assignment.teacher.username} "
                    f"to {assignment.subject.subject_name} ({assignment.school_class.class_name})."
                )
                return redirect('assign_teacher')
            else:
                # Display validation errors (such as "Already assigned")
                for field, errors in assignment_form.errors.items():
                    for error in errors:
                        messages.error(request, error)

        # 3. DELETE SINGLE ASSIGNMENT
        elif 'delete_assignment' in request.POST:
            assignment_id = request.POST.get('assignment_id')
            assignment = get_object_or_404(TeacherAssignment, id=assignment_id)
            subject_name = assignment.subject.subject_name
            class_name = assignment.school_class.class_name
            assignment.delete()
            messages.success(request, f"Assignment for {subject_name} ({class_name}) deleted.")
            return redirect('assign_teacher')

        # 4. RESET ACADEMIC YEAR (ARCHIVE ALL)
        elif 'reset_academic_year' in request.POST:
            year_label = request.POST.get('academic_year', f"{datetime.date.today().year}")
            
            # Move current assignments into archive table
            archived_count = 0
            for item in assignments:
                PreviousAssignment.objects.create(
                    teacher_name=item.teacher.get_full_name() or item.teacher.username,
                    class_name=item.school_class.class_name,
                    subject_name=item.subject.subject_name,
                    academic_year=year_label
                )
                archived_count += 1

            # Delete active assignments
            assignments.delete()
            messages.success(request, f"Academic year reset! {archived_count} assignment(s) moved to previous assignments archive ({year_label}).")
            return redirect('assign_teacher')

    context = {
        'teacher_form': teacher_form,
        'assignment_form': assignment_form,
        'assignments': assignments,
        'previous_assignments': previous_assignments,
    }
    return render(request, 'portal/assign_teacher.html', context)

#ACADEMIC SETUP
@user_passes_test(lambda u: u.is_authenticated and u.is_superuser, login_url='login')
def academic_setup(request):
    classes = SchoolClass.objects.all()
    subjects = Subject.objects.all()
    
    # Get or create the single configuration object
    config, created = AcademicConfiguration.objects.get_or_create(id=1)

    if request.method == 'POST':
        # 1. SET ACTIVE TERM
        if 'set_term' in request.POST:
            term_form = AcademicTermForm(request.POST)
            if term_form.is_valid():
                selected_term = int(term_form.cleaned_data['term'])
                config.current_term = selected_term
                config.save()
                messages.success(request, f"Academic Term updated to Term {selected_term}!")
                return redirect('academic_setup')

        # 2. ADD CLASS
        elif 'add_class' in request.POST:
            class_form = SchoolClassForm(request.POST)
            if class_form.is_valid():
                cls = class_form.save()
                messages.success(request, f"Class '{cls.class_name}' added successfully!")
                return redirect('academic_setup')

        # 3. ADD SUBJECT
        elif 'add_subject' in request.POST:
            subject_form = SubjectForm(request.POST)
            if subject_form.is_valid():
                subj = subject_form.save()
                messages.success(request, f"Subject '{subj.subject_name}' added successfully!")
                return redirect('academic_setup')

        # 4. DELETE SUBJECT
        elif 'delete_subject' in request.POST:
            subject_id = request.POST.get('subject_id')
            subj = get_object_or_404(Subject, id=subject_id)
            name = subj.subject_name
            subj.delete()
            messages.success(request, f"Subject '{name}' deleted successfully!")
            return redirect('academic_setup')

        # 5. DELETE CLASS    
        elif 'delete_class' in request.POST:
            class_id = request.POST.get('class_id')
            cls = get_object_or_404(SchoolClass, id=class_id)
            name = cls.class_name
            cls.delete()
            messages.success(request, f"class '{name}' deleted successfully!")
            return redirect('academic_setup')


    # Initialize forms with current values
    term_form = AcademicTermForm(initial={'term': config.current_term})
    class_form = SchoolClassForm()
    subject_form = SubjectForm()

    context = {
        'classes': classes,
        'subjects': subjects,
        'active_term': config.current_term,  # <-- Pass the term integer directly
        'class_form': class_form,
        'subject_form': subject_form,
        'term_form': term_form,
    }
    return render(request, 'portal/academic_setup.html', context)

@login_required
def student_report_card(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    school_class = student.school_class
    config, _ = AcademicConfiguration.objects.get_or_create(id=1)

    # 1. Fetch all students in this class
    class_students = Student.objects.filter(school_class=school_class)
    total_students_count = class_students.count()

    # 2. Calculate total marks for all students in class to determine rankings
    student_rankings = []
    for s in class_students:
        total_score = Grade.objects.filter(student=s).aggregate(total=Sum('marks'))['total'] or 0
        student_rankings.append({
            'student_id': s.id,
            'total_score': total_score
        })

    # Sort students by total score descending (highest total first)
    student_rankings.sort(key=lambda x: x['total_score'], reverse=True)

    # Find position of current student
    student_position = "-"
    student_total_marks = 0
    for rank, item in enumerate(student_rankings, start=1):
        if item['student_id'] == student.id:
            student_position = rank
            student_total_marks = item['total_score']
            break

    # 3. Get subject marks for this specific student
    all_subjects = Subject.objects.all()
    subject_report = []

    for subject in all_subjects:
        grade_record = Grade.objects.filter(student=student, subject=subject).first()
        score = grade_record.marks if grade_record else None
        grade_text = calculate_grade(score, school_class.class_name)

        subject_report.append({
            'subject_name': subject.subject_name,
            'score': score if score is not None else "-",
            'grade': grade_text
        })

    context = {
        'student': student,
        'school_class': school_class,
        'academic_term': config.current_term,
        'academic_year': config.academic_year,
        'total_students_count': total_students_count,
        'student_position': student_position,
        'student_total_marks': student_total_marks,
        'subject_report': subject_report,
    }
    return render(request, 'portal/student_report_card.html', context)

#PROMOTING STUDENTS TO THE NEXT CLASS
def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def promote_academic_year(request):
    if request.method == 'POST':
        new_academic_year = request.POST.get('new_academic_year')
        
        try:
            with transaction.atomic():
                # 1. Fetch Class Objects
                form_1 = SchoolClass.objects.get(class_name__iexact='Form 1')
                form_2 = SchoolClass.objects.get(class_name__iexact='Form 2')
                form_3 = SchoolClass.objects.get(class_name__iexact='Form 3')
                form_4 = SchoolClass.objects.get(class_name__iexact='Form 4')

                # 2. Convert QuerySets to static lists BEFORE modifying the DB
                # (Adjust 'current_class' below if your Student model uses 'school_class')
                form_4_students = list(Student.objects.filter(school_class=form_4))
                form_3_students = list(Student.objects.filter(school_class=form_3))
                form_2_students = list(Student.objects.filter(school_class=form_2))
                form_1_students = list(Student.objects.filter(school_class=form_1))

                # Step A: Graduate Form 4s (Mark inactive or keep class as archived)
                count_f4 = 0
                for s in form_4_students:
                    # If you have an is_active or is_graduated field:
                    # s.is_active = False
                    # s.save()
                    count_f4 += 1

                # Step B: Promote Form 3 -> Form 4
                count_f3 = 0
                for s in form_3_students:
                    s.school_class = form_4
                    s.save()
                    count_f3 += 1

                # Step C: Promote Form 2 -> Form 3
                count_f2 = 0
                for s in form_2_students:
                    s.school_class = form_3
                    s.save()
                    count_f2 += 1

                # Step D: Promote Form 1 -> Form 2
                count_f1 = 0
                for s in form_1_students:
                    s.school_class = form_2
                    s.save()
                    count_f1 += 1

                # Step E: Update System Academic Year & Reset Term
                config = AcademicConfiguration.objects.filter(is_active=True).first()
                if not config:
                    config = AcademicConfiguration.objects.first()
                if config:
                    config.academic_year = new_academic_year
                    config.current_term = 1
                    config.save()

                messages.success(
                    request,
                    f"Academic Year successfully updated to {new_academic_year}! "
                    f"Graduated Form 4s ({count_f4}), Promoted Form 3s ({count_f3}), "
                    f"Form 2s ({count_f2}), Form 1s ({count_f1})."
                )
                return redirect('admin_matrix')

        except Exception as e:
            messages.error(request, f"Promotion process failed: {str(e)}")

    return render(request, 'portal/promote_students.html')



