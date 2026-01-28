from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),

    
    path('student/register/', views.student_register, name='student_register'),
    path('teacher/register/', views.teacher_register, name='teacher_register'),
    path('student/login/', views.student_login, name='student_login'),
    path('teacher/login/', views.teacher_login, name='teacher_login'),
    path('logout/', views.logout_view, name='logout'),

   
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),

   
    path('quiz/create/', views.create_quiz, name='create_quiz'),
    path('quiz/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('quiz/<int:quiz_id>/add_question/', views.add_question, name='add_question'),
    path('quiz/<int:quiz_id>/preview/', views.preview_quiz, name='preview_quiz'),

    path('quiz/<int:quiz_id>/responses/', views.view_responses, name='view_responses'),

    
    path('quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('quiz/<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('quiz/<int:quiz_id>/result/', views.quiz_result, name='quiz_result'),

    
    path('student/quiz/submitted/', views.student_dashboard_submitted, name='student_dashboard_submitted'),  
]
