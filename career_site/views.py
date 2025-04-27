import json, logging
import os
from django.conf import settings
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
from .models import Question, Assessment, Answer, PersonalityResult
from .models import MasterClassCategory
from .models import CareerLibrary, CareerCategory, CareerSubCategory
from django.core.paginator import Paginator
from .models import Assessment, Question
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.urls import reverse
from career_site.forms import UserRegisterForm, StudentProfileForm, AdminProfileForm, QuestionForm

def home(request):
    if request.user.is_authenticated:
        if request.user.is_student:
            return redirect('dashboard')
        elif request.user.is_admin:
            return redirect('admin-dashboard')
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
    if request.user.assessments.filter(completed=True).exists():
        return redirect('assessment_results')
    
    assessment, created = Assessment.objects.get_or_create(
        user=request.user,
        completed=False
    )
    
    # Initialize answers for all questions if this is a new assessment
    if created:
        with transaction.atomic():
            for question in Question.objects.all():
                Answer.objects.get_or_create(
                    assessment=assessment,
                    question=question
                )
    
    questions = Question.objects.all().order_by('order')
    paginator = Paginator(questions, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get answered question IDs
    answered_question_ids = list(
        assessment.answers.exclude(choice__isnull=True)
        .values_list('question_id', flat=True)
    )
    
    return render(request, 'assessment.html', {
        'questions': page_obj,
        'assessment': assessment,
        'all_questions_count': questions.count(),
        'answered_count': assessment.get_answered_count(),
        'progress_percent': assessment.get_progress_percent(),
        'answered_question_ids': answered_question_ids,
    })

@login_required
@require_POST
def save_answers(request):
    page_action = request.POST.get('page_action', '')
    is_final_submit = request.POST.get('is_final_submit') == 'true'
    
    # Only process if this is the final submission
    if not is_final_submit:
        return JsonResponse({
            'success': True,
            'next_page': request.POST.get('next_page')
        })
    
    # On final submission, create or get assessment
    assessment, created = Assessment.objects.get_or_create(
        user=request.user,
        completed=False
    )
    
    try:
        with transaction.atomic():
            # Process all submitted answers
            for key, value in request.POST.items():
                if key.startswith('question_'):
                    question_id = key.split('_')[1]
                    Answer.objects.update_or_create(
                        assessment=assessment,
                        question_id=question_id,
                        defaults={'choice': bool(int(value))}
                    )
            
            # Mark assessment as complete
            assessment.completed = True
            assessment.save()
            
            # Calculate results
            result = calculate_personality_type(assessment)
            if not result:
                raise Exception("Could not calculate results")
            
            return JsonResponse({
                'success': True,
                'redirect_url': reverse('assessment_results')
            })
            
    except Exception as e:
        logger.error(f"Error saving answers: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def assessment_results(request):
    assessment = request.user.assessments.filter(completed=True).first()
    if not assessment:
        return redirect('start_assessment')
    
    try:
        result = assessment.result
    except PersonalityResult.DoesNotExist:
        result = calculate_personality_type(assessment)
        if not result:
            messages.error(request, "Could not calculate results. Please retake the assessment.")
            return redirect('start_assessment')
    
    return render(request, 'results.html', {
        'result': result,
        'assessment': assessment
    })


def download_results(request):
    try:
        # Get the latest assessment result for the user
        result = PersonalityResult.objects.filter(assessment__user=request.user).latest('date_created')
        
        # Prepare context data
        context = {
            'user': request.user,
            'date': result.date_created.strftime("%B %d, %Y"),
            'type_code': result.type_code,
            'title': result.title,
            'description': result.description,
            'strengths': result.get_strengths().replace('\n', '<br>'),
            'growth_areas': result.get_growth_areas().replace('\n', '<br>'),
            'career_suggestions': result.get_career_suggestions().replace('\n', '<br>'),
            'relationships': result.get_relationships().replace('\n', '<br>'),
            'famous_examples': result.get_famous_examples(),
            'chart_image': result.get_chart_image(),
            'dimensions': {
                'e_score': result.get_e_score(),
                'i_score': result.get_i_score(),
                's_score': result.get_s_score(),
                'n_score': result.get_n_score(),
                't_score': result.get_t_score(),
                'f_score': result.get_f_score(),
                'j_score': result.get_j_score(),
                'p_score': result.get_p_score(),
            }
        }
        
        # Render template
        template = get_template('pdf_results.html')
        html = template.render(context)
        
        # Create PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="personality_assessment_{request.user.username}.pdf"'
        
        pisa_status = pisa.CreatePDF(html, dest=response)
        
        if pisa_status.err:
            return HttpResponse('PDF generation error')
        return response

    except Exception as e:
        logger.error(f"PDF download error: {str(e)}", exc_info=True)
        return redirect('assessment_results')
    

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
    if Question.objects.count() >= 70:
        messages.error(request, "Maximum number of questions (70) has been reached.")
        return redirect('manage_questions')
    
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
    
    # Get personality type details
    try:
        personality_type = PersonalityResult.objects.get(type_code=result.personality_type)
    except PersonalityResult.DoesNotExist:
        personality_type = None
        logger.error(f"Personality type {result.personality_type} not found in database")
    
    answers = assessment.answers.all().order_by('question__order')
    
    return render(request, 'result_detail.html', {
        'assessment': assessment,
        'result': result,
        'personality_type': personality_type,
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
    
    # Get personality type details
    try:
        personality_type = PersonalityResult.objects.get(type_code=result.personality_type)
    except PersonalityResult.DoesNotExist:
        personality_type = None
        logger.error(f"Personality type {result.personality_type} not found in database")
    
    template_path = 'view_results.html'
    context = {
        'result': result,
        'assessment': assessment,
        'personality_type': personality_type,
        'admin_view': True
    }
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="assessment_report_{assessment.user.username}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Error generating PDF')
    return response