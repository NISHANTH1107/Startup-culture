import json, logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, StudentProfileForm, AdminProfileForm
from .models import User, StudentProfile, AdminProfile
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.views.decorators.csrf import csrf_protect
from .assessment_logic import calculate_personality_type  
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Question
from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Question, Assessment, Answer, PersonalityResult
from .models import MasterClassCategory
from .models import CareerLibrary, CareerCategory, CareerSubCategory


def home(request):
    return render(request, 'home.html')

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
        # Check if user has completed an assessment
        assessment_completed = request.user.assessments.filter(completed=True).exists()
        return render(request, 'user_dashboard.html', {
            'assessment_completed': assessment_completed
        })
    elif request.user.is_admin:
        return redirect('admin-dashboard')
    
    else:
        return redirect('home')

@login_required
def admin_dashboard(request):
    if not request.user.is_admin:
        return redirect('dashboard')
    return render(request, 'admin_dashboard.html')


def career_library(request):
    libraries = CareerLibrary.objects.all()
    return render(request, 'library.html', {'libraries': libraries})

def category_list(request, library_id):
    library = get_object_or_404(CareerLibrary, pk=library_id)
    categories = library.categories.all()
    return render(request, 'category_list.html', {
        'library': library,
        'categories': categories
    })

def career_detail(request, subcategory_id):
    career = get_object_or_404(CareerSubCategory, pk=subcategory_id)
    institutes = career.institutes.all()
    
    # Prepare chart data
    chart_data = {
        'labels': ['Current', 'Long Term', 'Very Long Term'],
        'datasets': [{
            'label': 'Career Demand',
            'data': [
                career.current_demand,
                career.long_term_demand,
                career.very_long_term_demand
            ],
            'backgroundColor': 'rgba(212, 175, 55, 0.5)',
            'borderColor': 'rgba(212, 175, 55, 1)',
            'borderWidth': 1
        }]
    }
    
    return render(request, 'career_detail.html', {
        'career': career,  # Note: Typo here should be 'career'
        'institutes': institutes,
        'chart_data': chart_data,
        'demand_labels': [  # Typo here - should be 'demand_labels'
            '', 'Extremely Low', 'Very Low', 'Low', 
            'Medium', 'High', 'Very High', 'Extremely High'
        ]
    })
    


def master_class_list(request):
    categories = MasterClassCategory.objects.all()
    # Get first 2 videos from each category for the overview
    for category in categories:
        category.preview_videos = category.videos.all()[:2]
    return render(request, 'list.html', {'categories': categories})

def master_class_detail(request, category_id):
    category = get_object_or_404(MasterClassCategory, pk=category_id)
    videos = category.videos.all()
    all_categories = MasterClassCategory.objects.all()  # For sidebar
    return render(request, 'detail.html', {
        'category': category,
        'videos': videos,
        'categories': all_categories
    })
    

@login_required
def start_assessment(request):
    # Check if user already has a completed assessment
    if request.user.assessments.filter(completed=True).exists():
        return redirect('assessment_results')
    
    # Create a new assessment if none exists
    assessment, created = Assessment.objects.get_or_create(
        user=request.user,
        completed=False
    )
    
    questions = Question.objects.all().order_by('order')
    return render(request, 'assessment.html', {
        'questions': questions,
        'assessment': assessment
    })

@login_required
def submit_assessment(request):
    if request.method == 'POST':
        try:
            assessment = Assessment.objects.get(
                user=request.user,
                completed=False
            )
            
            # Process answers
            assessment.answers.all().delete()
            for question in Question.objects.all():
                if choice := request.POST.get(f'question_{question.id}'):
                    Answer.objects.create(
                        assessment=assessment,
                        question=question,
                        choice=bool(int(choice))
                    )
            
            assessment.completed = True
            assessment.save()
            
            # Calculate result with error handling
            if not calculate_personality_type(assessment):
                messages.error(request, "Could not calculate results. Please try again.")
                return redirect('start_assessment')
            
            return redirect('assessment_results')
            
        except Exception as e:
            logger.error(f"Assessment submission error: {str(e)}")
            messages.error(request, "Error processing your assessment")
            return redirect('start_assessment')
    
    return redirect('start_assessment')

@login_required
def assessment_results(request):
    assessment = request.user.assessments.filter(completed=True).first()
    
    if not assessment:
        return redirect('start_assessment')
    
    try:
        result = assessment.result
    except PersonalityResult.DoesNotExist:
        # Calculate and create the result if it doesn't exist
        result = calculate_personality_type(assessment)
    
    return render(request, 'results.html', {
        'result': result,
        'assessment': assessment
    })

@login_required
def download_results(request):
    assessment = request.user.assessments.filter(completed=True).first()
    if not assessment:
        return redirect('start_assessment')
    
    try:
        result = assessment.result
    except PersonalityResult.DoesNotExist:
        result = calculate_personality_type(assessment)
    
    template_path = 'pdf_results.html'
    context = {'result': result, 'assessment': assessment}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="personality_assessment_{request.user.username}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'option_a', 'option_b', 'order']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'option_a': forms.TextInput(attrs={'class': 'form-control'}),
            'option_b': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'})
        }

def is_admin(user):
    return user.is_authenticated and user.is_admin

@login_required
@user_passes_test(is_admin)
def manage_questions(request):
    questions = Question.objects.all().order_by('order')
    return render(request, 'manage_questions.html', {
        'questions': questions,
        'section_title': 'Manage Assessment Questions'
    })

@login_required
def add_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question added successfully!')
            return redirect('manage_questions')
    else:
        # Set default order to be one more than the highest current order
        next_order = 1
        if Question.objects.exists():
            next_order = Question.objects.order_by('-order').first().order + 1
        form = QuestionForm(initial={'order': next_order})
    
    return render(request, 'question_form.html', {
        'form': form,
        'section_title': 'Add New Question'
    })

@login_required
@user_passes_test(is_admin)
def edit_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated successfully!')
            return redirect('manage_questions')
    else:
        form = QuestionForm(instance=question)
    
    return render(request, 'question_form.html', {
        'form': form,
        'question': question,
        'section_title': 'Edit Question'
    })

@login_required
@user_passes_test(is_admin)
def delete_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted successfully!')
        return redirect('manage_questions')
    
    return render(request, 'confirm_delete.html', {
        'question': question,
        'section_title': 'Delete Question'
    })

@login_required
@user_passes_test(is_admin)
def reorder_questions(request):
    if request.method == 'POST':
        question_ids = request.POST.getlist('question_ids[]')
        
        for i, question_id in enumerate(question_ids, 1):
            Question.objects.filter(pk=question_id).update(order=i)
        
        return redirect('manage_questions')
    
    questions = Question.objects.all().order_by('order')
    return render(request, 'reorder_questions.html', {
        'questions': questions,
        'section_title': 'Reorder Questions'
    })
    
@login_required
@user_passes_test(is_admin)
def view_results(request):
    assessments = Assessment.objects.filter(completed=True).order_by('-date_taken')
    
    return render(request, 'view_results.html', {
        'assessments': assessments,
        'section_title': 'Assessment Results'
    })

@login_required
@user_passes_test(is_admin)
def view_result_detail(request, assessment_id):
    assessment = get_object_or_404(Assessment, pk=assessment_id, completed=True)
    
    try:
        result = assessment.result
    except PersonalityResult.DoesNotExist:
        result = calculate_personality_type(assessment)
    
    answers = assessment.answers.all().order_by('question__order')
    
    return render(request, 'result_detail.html', {
        'assessment': assessment,
        'result': result,
        'answers': answers,
        'section_title': f'Result: {assessment.user.username}'
    })
    
@login_required
# @user_passes_test(is_admin)
def manage_users(request):
    students = User.objects.filter(is_student=True).select_related('studentprofile')
    
    # Add assessment status for each student
    student_data = []
    for student in students:
        latest_assessment = student.assessments.filter(completed=True).order_by('-date_taken').first()
        has_result = hasattr(latest_assessment, 'result') if latest_assessment else False
        
        student_data.append({
            'user': student,
            'profile': student.studentprofile,
            'has_assessment': latest_assessment is not None,
            'result': latest_assessment.result if has_result else None,
            'assessment_id': latest_assessment.id if latest_assessment else None
        })
    
    return render(request, 'manage_users.html', {
        'students': student_data,
        'section_title': 'Manage Students'
    })
    
@login_required
@user_passes_test(is_admin)
def admin_result_detail(request, assessment_id):
    assessment = get_object_or_404(Assessment, pk=assessment_id)
    result = assessment.result
    
    template_path = 'pdf_results.html'
    context = {
        'result': result,
        'assessment': assessment,
        'admin_view': True
    }
    
    response = HttpResponse(content_type='application/pdf')
    # Changed from 'attachment' to 'inline' to open in browser
    response['Content-Disposition'] = f'inline; filename="assessment_report_{assessment.user.username}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Error generating PDF')
    return response