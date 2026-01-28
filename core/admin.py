from django.contrib import admin
from django.utils import timezone
from .models import Quiz, Question, Option, QuizAttempt, Response, Result, Teacher, Student


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'start_time', 'end_time', 'is_active')
    list_filter = ('created_by', 'start_time', 'end_time')
    search_fields = ('name', 'description')

    def is_active(self, obj):
        return obj.start_time <= timezone.now() <= obj.end_time
    is_active.boolean = True
    is_active.short_description = 'Active'


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'text', 'correct_answer_display']

    def correct_answer_display(self, obj):
        correct_option = obj.options_set.filter(is_correct=True).first()
        return correct_option.option_text if correct_option else 'N/A'


    correct_answer_display.short_description = 'Correct Answer'


admin.site.register(Question, QuestionAdmin)


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('option_text', 'question', 'is_correct')
    list_filter = ('question', 'is_correct')
    search_fields = ('option_text',)


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'start_time_display', 'completed')
    list_filter = ('quiz', 'completed')
    search_fields = ('student__username', 'quiz__name')

    def start_time_display(self, obj):
        return obj.started_at
    start_time_display.admin_order_field = 'started_at'
    start_time_display.short_description = 'Start Time'


class QuizFilter(admin.SimpleListFilter):
    title = 'Quiz'
    parameter_name = 'quiz'

    def lookups(self, request, model_admin):
        quizzes = Quiz.objects.all()
        return [(quiz.id, quiz.name) for quiz in quizzes]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(attempt__quiz__id=self.value())
        return queryset


class StudentFilter(admin.SimpleListFilter):
    title = 'Student'
    parameter_name = 'student'

    def lookups(self, request, model_admin):
        students = Student.objects.all()
        return [(student.id, student.user.username) for student in students]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(attempt__student__id=self.value())
        return queryset


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('student_display', 'question', 'selected_option', 'quiz_attempt_display')
    list_filter = (QuizFilter, StudentFilter)
    search_fields = ('student__user__username', 'question__text')

    def student_display(self, obj):
        return obj.student.user.username if obj.student and obj.student.user else 'N/A'

    def quiz_attempt_display(self, obj):
        return obj.attempt.quiz.name if obj.attempt and obj.attempt.quiz else 'N/A'
    quiz_attempt_display.short_description = 'Quiz Attempt'


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student_display', 'quiz', 'score', 'total_questions_display')
    list_filter = ('quiz', 'student')
    search_fields = ('student__username', 'quiz__name')

    def student_display(self, obj):
        return obj.student.username if obj.student else 'N/A'

    def total_questions_display(self, obj):
        return obj.quiz.questions.count() if obj.quiz else 0
    total_questions_display.short_description = 'Total Questions'
