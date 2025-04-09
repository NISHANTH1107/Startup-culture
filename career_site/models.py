from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
import base64
import io
import matplotlib.pyplot as plt
from django.db import models

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
    

class MasterClassCategory(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Master Class Categories"
        ordering = ['order']
    
    def __str__(self):
        return self.title

class MasterClassVideo(models.Model):
    category = models.ForeignKey(MasterClassCategory, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    youtube_id = models.CharField(max_length=20, help_text="YouTube video ID (11 characters)")
    description = models.TextField(blank=True)
    duration = models.CharField(max_length=20, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.category.title} - {self.title}"

User = get_user_model()

class Question(models.Model):
    text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Question {self.order}: {self.text[:50]}..."

class Assessment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessments')
    date_taken = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Assessment for {self.user.username} on {self.date_taken}"

class Answer(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.BooleanField()  # True for B, False for A
    
    def __str__(self):
        return f"Answer to Q{self.question.order}: {'B' if self.choice else 'A'}"

class PersonalityResult(models.Model):
    assessment = models.OneToOneField(Assessment, on_delete=models.CASCADE, related_name='result')
    personality_type = models.CharField(max_length=4)  # e.g., "ENTJ"
    ei_score = models.IntegerField()  # E score minus I score
    sn_score = models.IntegerField()  # S score minus N score
    tf_score = models.IntegerField()  # T score minus F score
    jp_score = models.IntegerField()  # J score minus P score
    date_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.personality_type} result for {self.assessment.user.username}"
        
    def get_e_score(self):
        return (self.ei_score + 100) // 2
    
    def get_i_score(self):
        return 100 - self.get_e_score()
    
    def get_s_score(self):
        return (self.sn_score + 100) // 2
    
    def get_n_score(self):
        return 100 - self.get_s_score()
    
    def get_t_score(self):
        return (self.tf_score + 100) // 2
    
    def get_f_score(self):
        return 100 - self.get_t_score()
    
    def get_j_score(self):
        return (self.jp_score + 100) // 2
    
    def get_p_score(self):
        return 100 - self.get_j_score()
    
    def get_type_description(self):
        # Return description based on type
        descriptions = {
            "ISTJ": "The Inspector - Practical and fact-minded individuals, reliable, detail-oriented, and value tradition.",
            "ISFJ": "The Protector - Dedicated, warm, and protective, with a strong sense of duty and incredible attention to detail.",
            "INFJ": "The Counselor - Idealistic, creative, and caring, seeking meaning and connection in ideas and relationships.",
            "INTJ": "The Mastermind - Strategic, logical, and innovative with a drive for improvement and implementation of ideas.",
            "ISTP": "The Craftsman - Bold, practical experimenters, masters of tools and materials, with a spontaneous nature.",
            "ISFP": "The Composer - Warm, sensitive, and imaginative individuals who live in the present and value personal freedom.",
            "INFP": "The Healer - Idealistic, loyal, and deeply empathetic, with strong values and dedication to their beliefs.",
            "INTP": "The Architect - Logical, original thinkers with a drive to understand the universe and its principles.",
            "ESTP": "The Dynamo - Energetic, action-oriented risk-takers who solve problems with practical solutions.",
            "ESFP": "The Performer - Spontaneous, energetic, and enthusiastic individuals who enjoy people and experiences.",
            "ENFP": "The Champion - Enthusiastic, creative, and sociable free spirits who find connections between people and ideas.",
            "ENTP": "The Visionary - Quick, ingenious, and outspoken, with an ability to connect concepts and people.",
            "ESTJ": "The Supervisor - Practical, traditional, and organized, with a focus on getting things done efficiently.",
            "ESFJ": "The Provider - Warm-hearted, conscientious, and cooperative, seeking harmony in their environment.",
            "ENFJ": "The Teacher - Charismatic, empathetic leaders, responsive to others' needs and societal expectations.",
            "ENTJ": "The Commander - Bold, imaginative, and strong-willed leaders who always find a way or make one.",
        }
        return descriptions.get(self.personality_type, "No description available.")
    
    def get_chart_image(self):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        # Generate radar chart and return as base64
        dimensions = ['E', 'I', 'S', 'N', 'T', 'F', 'J', 'P']
        scores = [
            self.get_e_score(), self.get_i_score(),
            self.get_s_score(), self.get_n_score(),
            self.get_t_score(), self.get_f_score(),
            self.get_j_score(), self.get_p_score()
        ]
        
        try:
            fig = plt.figure(figsize=(8, 8))
            ax = fig.add_subplot(111, polar=True)
            
            angles = [n / 8 * 2 * 3.141592653589793 for n in range(8)]
            angles += angles[:1]
            
            scores += scores[:1]
            ax.plot(angles, scores, linewidth=1, linestyle='solid')
            ax.fill(angles, scores, 'b', alpha=0.1)
            
            ax.set_thetagrids([n * 45 for n in range(8)], dimensions)
            ax.set_ylim(0, 100)
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            plt.close(fig)  # Explicitly close the figure
            buf.seek(0)
            return base64.b64encode(buf.read()).decode('utf-8')
        except Exception as e:
            print(f"Error generating chart: {str(e)}")
            return ""