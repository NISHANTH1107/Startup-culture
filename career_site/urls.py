from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    
    # Profile URLs
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.profile_update, name='profile-update'),
    
    # Dashboard URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
    
    # Home URL
    path('', views.home, name='home'),
    
    # Career Library URLs
    path('library/', views.career_library, name='career_library'),  # Removed leading slash
    path('library/<int:library_id>/', views.category_list, name='category_list'),
    path('career/<int:subcategory_id>/', views.career_detail, name='career_detail'),
    
    # Master Class URLs
    path('master-class/', views.master_class_list, name='master_class_list'),
    path('master-class/<int:category_id>/', views.master_class_detail, name='master_class_detail'),
    
    # Assessment URLs
    path('assessment/', views.start_assessment, name='start_assessment'),
    path('assessment/save/', views.save_answers, name='save_answers'),
    # path('assessment/submit/', views.submit_assessment, name='submit_assessment'),
    path('assessment/results/', views.assessment_results, name='assessment_results'),
    path('assessment/download/', views.download_results, name='download_results'),
    
    
    # Admin Question Management URLs
    path('admin/questions/', views.manage_questions, name='manage_questions'),
    path('admin/questions/add/', views.add_question, name='add_question'),  # Changed to be under admin/questions
    path('admin/questions/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('admin/questions/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('admin/questions/reorder/', views.reorder_questions, name='reorder_questions'),
    
    # Results URLs
    path('admin/results/', views.view_results, name='view_results'),
    path('admin/results/<int:assessment_id>/', views.view_result_detail, name='view_result_detail'),
    
    #manage users URLs
    path('admin/users/', views.manage_users, name='manage_users'),
    path('admin/results/<int:assessment_id>/pdf/', views.admin_result_detail, name='admin_result_detail'),
    
    path('open-assessment/', views.open_assessment, name='open_assessment'),
    path('webhook/', views.webhook, name='webhook'),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)