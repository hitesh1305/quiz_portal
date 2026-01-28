from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher', null=True, blank=True, default=None)

    def __str__(self):
        return self.user.username if self.user else "Unnamed Teacher"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student', null=True, blank=True, default=None)

    def __str__(self):
        return self.user.username if self.user else "Unnamed Student"

class Quiz(models.Model):
    name = models.CharField(max_length=255, default="Untitled Quiz")
    description = models.TextField(blank=True, null=True, default="")
    created_by = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True, default=None)
    start_time = models.DateTimeField(default=timezone.now, null=True, blank=True)
    end_time = models.DateTimeField(default=timezone.now, null=True, blank=True)
    active = models.BooleanField(default=True)
    duration = models.IntegerField(default=30)  # Duration in minutes
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    text = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.text} ({self.quiz.name})"

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options_set', null=True, blank=True)
    option_text = models.CharField(max_length=255, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.option_text} {'(Correct)' if self.is_correct else ''}"

class QuizAttempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True, blank=True)
    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(default=timezone.now, null=True, blank=True)

    def __str__(self):
        return f"{self.student.username} - {self.quiz.name}"

class Response(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE,null=True, blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE,null=True, blank=True)
    selected_option = models.ForeignKey(Option, on_delete=models.CASCADE,null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE,null=True, blank=True)  # Ensure this line exists and is correct
    
    def __str__(self):
        return f"Response by {self.student} for {self.question.text}"

class Result(models.Model):
    attempt = models.OneToOneField(QuizAttempt, on_delete=models.CASCADE, null=True, blank=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    score = models.IntegerField(default=0)
    total_attempted = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.student.username} - {self.quiz.name}: {self.score}/{self.total_attempted}"
