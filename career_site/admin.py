from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, StudentProfile, AdminProfile, 
    CareerLibrary, CareerCategory, CareerSubCategory, TopInstitute,
    Question, Assessment, Answer, PersonalityResult,
    MasterClassCategory, MasterClassVideo
)

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


class TopInstituteInline(admin.TabularInline):
    model = TopInstitute
    extra = 1

class CareerSubCategoryAdmin(admin.ModelAdmin):
    inlines = [TopInstituteInline]

admin.site.register(CareerLibrary)
admin.site.register(CareerCategory)
admin.site.register(CareerSubCategory, CareerSubCategoryAdmin)

# Assessment-related admin configurations
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('order', 'text_preview', 'option_a', 'option_b')
    list_display_links = ('text_preview',)
    list_editable = ('order',)
    ordering = ('order',)
    search_fields = ('text', 'option_a', 'option_b')
    
    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Question Text'

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('question', 'choice')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

class PersonalityResultInline(admin.StackedInline):
    model = PersonalityResult
    extra = 0
    readonly_fields = ('personality_type', 'ei_score', 'sn_score', 'tf_score', 'jp_score', 'date_created')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_taken', 'completed', 'get_personality_type')
    list_filter = ('completed', 'date_taken')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('date_taken',)
    inlines = [AnswerInline, PersonalityResultInline]
    
    def get_personality_type(self, obj):
        if hasattr(obj, 'result'):
            return obj.result.personality_type
        return None
    get_personality_type.short_description = 'Personality Type'

class MasterClassVideoInline(admin.TabularInline):
    model = MasterClassVideo
    extra = 1

class MasterClassCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    list_editable = ('order',)
    inlines = [MasterClassVideoInline]

# Register assessment-related models
admin.site.register(Question, QuestionAdmin)
admin.site.register(Assessment, AssessmentAdmin)
admin.site.register(PersonalityResult)
admin.site.register(MasterClassCategory, MasterClassCategoryAdmin)
admin.site.register(MasterClassVideo)