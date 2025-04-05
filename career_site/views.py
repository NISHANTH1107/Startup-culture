from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, StudentProfileForm, AdminProfileForm
from .models import User, StudentProfile, AdminProfile

def home(request):
    return render(request, 'home.html')

from django.views.decorators.csrf import csrf_protect

@csrf_protect
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user_type = request.POST.get('user_type', 'student')  # Default to student
            
            if user_type == 'admin':
                user.is_admin = True
            else:
                user.is_student = True
                
            user.save()
            
            # Create corresponding profile
            if user.is_admin:
                AdminProfile.objects.create(user=user)
            else:
                StudentProfile.objects.create(user=user)
                
            messages.success(request, 'Registration successful!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    
    return render(request, 'register.html', {'form': form})

@login_required
def profile(request):
    if request.user.is_student:
        profile = request.user.studentprofile
    elif request.user.is_admin:
        profile = request.user.adminprofile
    else:
        profile = None
    return render(request, 'profile.html', {'profile': profile})

@login_required
def profile_update(request):
    if request.user.is_student:
        profile = request.user.studentprofile
        form_class = StudentProfileForm
    elif request.user.is_admin:
        profile = request.user.adminprofile
        form_class = AdminProfileForm
    else:
        return redirect('profile')
    
    if request.method == 'POST':
        form = form_class(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = form_class(instance=profile)
    
    return render(request, 'profile_update.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.is_student:
        return render(request, 'user_dashboard.html')
    elif request.user.is_admin:
        return redirect('admin-dashboard')
    else:
        return redirect('home')

@login_required
def admin_dashboard(request):
    if not request.user.is_admin:
        return redirect('dashboard')
    return render(request, 'admin_dashboard.html')