from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),    
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.profile_update, name='profile-update'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('', views.home, name='home'),
    path('/library', views.career_library, name='career_library'),
    path('library/<int:library_id>/', views.category_list, name='category_list'),
    path('career/<int:subcategory_id>/', views.career_detail, name='career_detail'),
    path('master-class/', views.master_class_list, name='master_class_list'),
    path('master-class/<int:category_id>/', views.master_class_detail, name='master_class_detail'),
]