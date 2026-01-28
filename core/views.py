from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.utils.timezone import now
from .models import (
    Quiz, Question, Option, QuizAttempt,
    Response, Result, Teacher, Student
)
from .forms import (
    StudentRegistrationForm, TeacherRegistrationForm,
    QuizForm, QuestionForm
)

def landing(request):
    return render(request, 'core/landing.html')


def student_register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            Student.objects.create(user=user)
            login(request, user)
            return redirect('student_dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'core/student_register.html', {'form': form})

def teacher_register(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            Teacher.objects.create(user=user)
            login(request, user)
            return redirect('teacher_dashboard')
    else:
        form = TeacherRegistrationForm()
    return render(request, 'core/teacher_register.html', {'form': form})

def student_login(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('student_dashboard')
    return render(request, 'core/student_login.html', {'form': form})

def teacher_login(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('teacher_dashboard')
    return render(request, 'core/teacher_login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('landing')

@login_required
def student_dashboard(request):
    student_user = request.user
    submitted_quizzes = Quiz.objects.filter(quizattempt__student=student_user, quizattempt__completed=True).distinct()
    available_quizzes = Quiz.objects.filter(
        start_time__lte=now(), end_time__gte=now(), active=True
    ).exclude(id__in=submitted_quizzes.values_list('id', flat=True))

    results = {
        result.quiz.id: result.score
        for result in Result.objects.filter(student=student_user)
    }

    return render(request, 'core/student_dashboard.html', {
        'available_quizzes': available_quizzes,
        'submitted_quizzes': submitted_quizzes,
        'results': results,
    })

@login_required
def teacher_dashboard(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    quizzes = Quiz.objects.filter(created_by=teacher)
    return render(request, 'core/teacher_dashboard.html', {'quizzes': quizzes})

@login_required
def create_quiz(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.created_by = teacher
            quiz.save()
            return redirect('teacher_dashboard')
    else:
        form = QuizForm()
    return render(request, 'core/create_quiz.html', {'form': form})

@login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by__user=request.user)
    quiz.delete()
    return redirect('teacher_dashboard')

@login_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        question_text = request.POST.get('question')
        options = request.POST.getlist('options[]')
        correct_option_index = request.POST.get('correct_option')

        if correct_option_index is not None:
            correct_option_index = int(correct_option_index)
            question = Question.objects.create(quiz=quiz, text=question_text)
            for i, option_text in enumerate(options):
                Option.objects.create(
                    question=question,
                    option_text=option_text,
                    is_correct=(i == correct_option_index),
                    order=i + 1
                )
            return render(request, 'core/add_question.html', {
                'quiz': quiz,
                'question_added': True
            })

    return render(request, 'core/add_question.html', {'quiz': quiz})

@login_required
def preview_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.prefetch_related('options_set')

    quiz_data = []
    for question in questions:
        options = question.options_set.all().order_by('order')
        quiz_data.append({
            'question': question,
            'options': options
        })

    return render(request, 'core/preview_quiz.html', {
        'quiz': quiz,
        'quiz_data': quiz_data
    })

from django.shortcuts import render, redirect, get_object_or_404
from .models import Quiz, QuizAttempt, Response
from django.contrib.auth.decorators import login_required

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    
    attempt = QuizAttempt.objects.filter(student=request.user, quiz=quiz, completed=False).first()

    
    if not attempt:
        attempt = QuizAttempt.objects.create(student=request.user, quiz=quiz)

    questions = quiz.questions.prefetch_related('options_set')

    if request.method == 'POST':
        
        for question in questions:
            selected_option_id = request.POST.get(f'question_{question.id}')
            if selected_option_id:
                try:
                    selected_option = Option.objects.get(id=selected_option_id, question=question)
                    Response.objects.create(
                        attempt=attempt,
                        question=question,
                        selected_option=selected_option
                    )
                except Option.DoesNotExist:
                    continue

      
        attempt.completed = True
        attempt.save()

        return redirect('quiz_result', quiz_id=quiz.id)

    return render(request, 'core/take_quiz.html', {'quiz': quiz, 'questions': questions, 'attempt': attempt})

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import Quiz, QuizAttempt, Response, Result

@login_required
def quiz_result(request, quiz_id):
    quiz    = get_object_or_404(Quiz, id=quiz_id)
    attempt = get_object_or_404(QuizAttempt,
                                student=request.user,
                                quiz=quiz,
                                completed=True)

    responses = Response.objects.filter(attempt=attempt) \
                                .select_related('question', 'selected_option')

    
    total_questions = quiz.questions.count()

   
    score = responses.filter(selected_option__is_correct=True).count()

    Result.objects.update_or_create(
        attempt=attempt,
        defaults={
            'quiz': quiz,
            'student': request.user,
            'score': score,
            'total_attempted': responses.count(),
        }
    )

    return render(request, 'core/quiz_result.html', {
        'quiz': quiz,
        'responses': responses,
        'score': score,
        'total': total_questions,   
        'attempt': attempt
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Quiz, Result

@login_required
def view_responses(request, quiz_id):
   
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by__user=request.user)

   
    results = (
        Result.objects
        .filter(quiz=quiz)
        .select_related('student')  
        .order_by('-score')         
    )

    return render(request, 'core/view_responses.html', {
        'quiz': quiz,
        'results': results,
    })
@login_required
def student_dashboard_submitted(request):
    student = request.user
    results = Result.objects.filter(student=student)
    attempted_quizzes = [{
        'quiz': result.quiz,
        'score': result.score,
        'attempted_at': result.created_at
    } for result in results]

    return render(request, 'core/student_dashboard_submitted.html', {
        'attempted_quizzes': attempted_quizzes
    })

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Quiz, QuizAttempt, Response, Option

@login_required
def submit_quiz(request, quiz_id):
    quiz    = get_object_or_404(Quiz, id=quiz_id)
    attempt = QuizAttempt.objects.filter(student=request.user, quiz=quiz, completed=False).first()
    if not attempt:
        return redirect('quiz_result', quiz_id=quiz.id)

    if request.method == 'POST':
       
        Response.objects.filter(attempt=attempt).delete()

        
        for question in quiz.questions.all():
            sel_id = request.POST.get(f"question_{question.id}")
            if sel_id:
                opt = get_object_or_404(Option, id=sel_id, question=question)
                Response.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_option=opt
                )

       
        attempt.completed = True
        attempt.save()

        return redirect('quiz_result', quiz_id=quiz.id)

   
    return redirect('take_quiz', quiz_id=quiz.id)
