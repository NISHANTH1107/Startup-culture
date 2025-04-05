from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StudentProfile, AdminProfile

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'is_student', 'is_admin')
    list_filter = ('is_student', 'is_admin')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'phone', 'date_of_birth')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_student', 'is_admin')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(StudentProfile)
admin.site.register(AdminProfile)
from django.contrib import admin
from .models import CareerLibrary, CareerCategory, CareerSubCategory, TopInstitute

class TopInstituteInline(admin.TabularInline):
    model = TopInstitute
    extra = 1

class CareerSubCategoryAdmin(admin.ModelAdmin):
    inlines = [TopInstituteInline]

admin.site.register(CareerLibrary)
admin.site.register(CareerCategory)
admin.site.register(CareerSubCategory, CareerSubCategoryAdmin)