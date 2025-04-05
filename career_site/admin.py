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