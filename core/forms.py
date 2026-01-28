from django import forms
from django.contrib.auth.models import User
from .models import Quiz, Question, Option


class StudentRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('confirm_password'):
            self.add_error('confirm_password', "Passwords must match.")
        return cleaned


class TeacherRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('confirm_password'):
            self.add_error('confirm_password', "Passwords must match.")
        return cleaned


class QuizForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=True
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=True
    )

    class Meta:
        model = Quiz
        fields = ['name', 'description', 'start_time', 'end_time']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['quiz', 'text']  # Include only the fields you want in the form


    option_1 = forms.CharField(max_length=255, required=True)
    option_2 = forms.CharField(max_length=255, required=True)
    option_3 = forms.CharField(max_length=255, required=True)
    option_4 = forms.CharField(max_length=255, required=True)
    correct_answer = forms.CharField(max_length=255, required=True)
    
    def save(self, commit=True):
        
        question = super().save(commit=False)
        
        if commit:
            question.save() 
        Option.objects.create(
            question=question, 
            option_text=self.cleaned_data['option_1'], 
            is_correct=self.cleaned_data['correct_answer'] == self.cleaned_data['option_1']
        )
        Option.objects.create(
            question=question, 
            option_text=self.cleaned_data['option_2'], 
            is_correct=self.cleaned_data['correct_answer'] == self.cleaned_data['option_2']
        )
        Option.objects.create(
            question=question, 
            option_text=self.cleaned_data['option_3'], 
            is_correct=self.cleaned_data['correct_answer'] == self.cleaned_data['option_3']
        )
        Option.objects.create(
            question=question, 
            option_text=self.cleaned_data['option_4'], 
            is_correct=self.cleaned_data['correct_answer'] == self.cleaned_data['option_4']
        )
        
        return question
