from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.username

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    education_level = models.CharField(max_length=100)
    interests = models.TextField()
    skills = models.TextField()
    career_goals = models.TextField()
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.user.username}'s Admin Profile"
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class CareerLibrary(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='career_library/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class CareerCategory(models.Model):
    library = models.ForeignKey(CareerLibrary, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='career_categories/', blank=True, null=True)
    card_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.library.title} - {self.name}"

class CareerSubCategory(models.Model):
    category = models.ForeignKey(CareerCategory, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    summary = models.TextField()
    daily_tasks = models.TextField(help_text="Bullet points separated by newlines")
    image = models.ImageField(upload_to='career_subcategories/', blank=True, null=True)
    
    # Career prospects data for chart
    current_demand = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        help_text="1=Extremely Low, 7=Extremely High"
    )
    long_term_demand = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(7)]
    )
    very_long_term_demand = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(7)]
    )

    def __str__(self):
        return f"{self.category.name} - {self.name}"

class TopInstitute(models.Model):
    career = models.ForeignKey(CareerSubCategory, on_delete=models.CASCADE, related_name='institutes')
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    is_private = models.BooleanField(default=True)
    rating = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        blank=True, null=True
    )

    def __str__(self):
        return f"{self.name} ({self.location})"