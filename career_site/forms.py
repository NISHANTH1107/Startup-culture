from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, StudentProfile, AdminProfile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'date_of_birth', 'password1', 'password2']

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['education_level', 'interests', 'skills', 'career_goals']

class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = AdminProfile
        fields = ['position', 'department']

class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)