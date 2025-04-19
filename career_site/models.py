from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
import base64
import io
import matplotlib.pyplot as plt
from django.db import models
import logging, matplotlib
from career_site.utils import generate_personality_chart


# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

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
    
    def get_answered_count(self):
        return self.answers.exclude(choice__isnull=True).count()
    
    def get_progress_percent(self):
        total = Question.objects.count()
        return int((self.get_answered_count() / total) * 100) if total else 0

class Answer(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.BooleanField(null=True, blank=True)  # Changed to allow null
    
    class Meta:
        unique_together = ('assessment', 'question')
    
    def __str__(self):
        return f"Answer to Q{self.question.order}: {'B' if self.choice else 'A' if self.choice is not None else 'Unanswered'}"

class PersonalityResult(models.Model):
    assessment = models.OneToOneField(
        'Assessment', 
        on_delete=models.CASCADE,
        related_name='result',
        primary_key=True
    )
    type_code = models.CharField(max_length=4)
    title = models.CharField(max_length=100)
    description = models.TextField()
    strengths = models.TextField()
    growth_areas = models.TextField()
    career_suggestions = models.TextField()
    relationships = models.TextField()
    famous_examples = models.TextField()
    banner_color = models.CharField(max_length=7, default='#D4AF37')
    
    raw_e_score = models.IntegerField(null=True, blank=True)
    raw_i_score = models.IntegerField(null=True, blank=True)
    raw_s_score = models.IntegerField(null=True, blank=True)
    raw_n_score = models.IntegerField(null=True, blank=True)
    raw_t_score = models.IntegerField(null=True, blank=True)
    raw_f_score = models.IntegerField(null=True, blank=True)
    raw_j_score = models.IntegerField(null=True, blank=True)
    raw_p_score = models.IntegerField(null=True, blank=True)
    personality_type = models.CharField(max_length=4)  # Already exists
    column_stats = models.JSONField(null=True, blank=True)  # For any statistical data
    
    # Add score fields
    ei_score = models.IntegerField(null=True, blank=True)
    sn_score = models.IntegerField(null=True, blank=True)
    tf_score = models.IntegerField(null=True, blank=True)
    jp_score = models.IntegerField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type_code} result for {self.assessment.user.username}"

    @classmethod
    def get_type_data(cls):
        return {
            "ISTJ": {
                "title": "The Logistician",
                "description": "Practical and fact-minded individuals, whose reliability cannot be doubted. They are thorough, responsible, and systematic, making them excellent at managing and executing tasks.",
                "strengths": "1. Honest and direct\n2. Strong-willed and dutiful\n3. Responsible and reliable\n4. Calm and practical\n5. Create and enforce order",
                "growth_areas": "1. Being more open to unconventional ideas\n2. Expressing emotions more freely\n3. Being more flexible with change\n4. Considering alternative perspectives\n5. Taking more risks",
                "career_suggestions": "1. Business Administration\n2. Finance\n3. Law\n4. Public Administration\n5. Accounting\n6. Military Science\n7. Criminal Justice\n8. Project Management",
                "relationships": "ISTJs are loyal and dependable partners who value stability and tradition. They show love through practical actions rather than words. They may struggle with emotional expression but are deeply committed to their relationships.",
                "famous_examples": "Queen Elizabeth II, George Washington, Natalie Portman, Warren Buffett, Angela Merkel"
            },
            "ISFJ": {
                "title": "The Defender",
                "description": "Warm, caring, and protective individuals who are always ready to defend their loved ones. They are extremely reliable, patient, and practical with a strong sense of duty.",
                "strengths": "1. Supportive and reliable\n2. Warm and considerate\n3. Practical and responsible\n4. Detailed and thorough\n5. Loyal and committed",
                "growth_areas": "1. Setting healthy boundaries\n2. Saying no without guilt\n3. Handling criticism better\n4. Being more assertive\n5. Taking more personal time",
                "career_suggestions": "1. Elementary Education\n2. Healthcare Administration\n3. Nursing\n4. Human Resources\n5. Social Work\n6. Counseling\n7. Library Science\n8. Nutrition/Dietetics",
                "relationships": "ISFJs are nurturing partners who express love through acts of service. They prioritize their partner's needs, sometimes at their own expense. They value stability and may struggle with conflict.",
                "famous_examples": "Mother Teresa, Kate Middleton, Rosa Parks, Dr. Watson (Sherlock Holmes), Laura Bush"
            },
            "INFJ": {
                "title": "The Advocate",
                "description": "Creative and compassionate individuals with strong intuition and deep convictions. They have a talent for helping others achieve potential while pursuing their own ideals.",
                "strengths": "1. Creative and insightful\n2. Principled and passionate\n3. Altruistic and empathetic\n4. Decisive and determined\n5. Organized and future-oriented",
                "growth_areas": "1. Being less perfectionistic\n2. Setting realistic expectations\n3. Sharing personal needs\n4. Handling criticism better\n5. Balancing idealism with practicality",
                "career_suggestions": "1. Psychology\n2. Education\n3. Public Health\n4. Organizational Leadership\n5. Counseling\n6. Social Work\n7. Theology/Religious Studies\n8. Human Rights",
                "relationships": "INFJs seek deep, meaningful connections and are intensely loyal. They may idealize relationships and need to communicate their needs more directly. They value emotional intimacy and shared values.",
                "famous_examples": "Nelson Mandela, Carl Jung, Martin Luther King Jr., Emily Brontë, Mother Teresa"
            },
            "INTJ": {
                "title": "The Architect",
                "description": "Strategic, analytical thinkers with a clear vision of how things should be. They are highly independent, confident, and self-motivated with a strong drive to implement their ideas.",
                "strengths": "1. Rational and quick-witted\n2. Independent and decisive\n3. Hardworking and determined\n4. Open-minded and imaginative\n5. Honest and direct",
                "growth_areas": "1. Being more open to emotions\n2. Considering others' feelings\n3. Practicing patience\n4. Accepting imperfections\n5. Valuing social rituals",
                "career_suggestions": "1. Strategic Management\n2. Economics\n3. Law\n4. International Business\n5. Computer Science\n6. Engineering\n7. Physics\n8. Mathematics",
                "relationships": "INTJs value intellectual connection and personal growth in relationships. They may struggle with emotional expression but are deeply loyal. They need partners who respect their independence.",
                "famous_examples": "Elon Musk, Friedrich Nietzsche, Ruth Bader Ginsburg, Stephen Hawking, Mark Zuckerberg"
            },
            "ISTP": {
                "title": "The Virtuoso",
                "description": "Bold and practical experimenters who excel at using tools and solving problems with hands-on approaches. They are spontaneous, adaptable, and masters of any situation.",
                "strengths": "1. Optimistic and energetic\n2. Creative and practical\n3. Spontaneous and rational\n4. Knowledgable about tools\n5. Excellent in crises",
                "growth_areas": "1. Considering long-term consequences\n2. Developing follow-through\n3. Expressing emotions better\n4. Valuing commitments more\n5. Planning ahead",
                "career_suggestions": "1. Engineering\n2. Computer Science\n3. Aviation\n4. Criminal Justice\n5. Sports Science\n6. Architecture\n7. Industrial Design\n8. Emergency Medicine",
                "relationships": "ISTPs are exciting but independent partners who value personal freedom. They show love through shared activities rather than words. They may struggle with emotional conversations.",
                "famous_examples": "Bruce Lee, Michael Jordan, Amelia Earhart, Clint Eastwood, Tom Cruise"
            },
            "ISFP": {
                "title": "The Adventurer",
                "description": "Flexible and charming artists who live in the present moment. They are sensitive, caring, and deeply attuned to their environment and personal values.",
                "strengths": "1. Charming and sensitive\n2. Imaginative and artistic\n3. Passionate and curious\n4. Practical and hands-on\n5. Loyal and committed",
                "growth_areas": "1. Being more assertive\n2. Handling conflict better\n3. Planning for the future\n4. Setting clearer boundaries\n5. Valuing structure more",
                "career_suggestions": "1. Fine Arts\n2. Graphic Design\n3. Interior Design\n4. Fashion Design\n5. Music\n6. Photography\n7. Culinary Arts\n8. Physical Therapy",
                "relationships": "ISFPs are warm, caring partners who value harmony. They express love through thoughtful actions and quality time. They may avoid confrontation and need personal space.",
                "famous_examples": "Michael Jackson, Frida Kahlo, Britney Spears, Wolfgang Amadeus Mozart, Jacqueline Kennedy Onassis"
            },
            "INFP": {
                "title": "The Mediator",
                "description": "Poetic, kind-hearted individuals who are guided by their values and ideals. They seek meaning in everything and want to make the world a better place.",
                "strengths": "1. Empathetic and caring\n2. Creative and imaginative\n3. Open-minded and curious\n4. Loyal and committed\n5. Idealistic and principled",
                "growth_areas": "1. Being more assertive\n2. Setting practical goals\n3. Handling criticism better\n4. Avoiding perfectionism\n5. Managing time effectively",
                "career_suggestions": "1. Creative Writing\n2. Literature\n3. Social Work\n4. Human Rights\n5. Psychology\n6. Counseling\n7. Environmental Studies\n8. Philosophy",
                "relationships": "INFPs seek deep, authentic connections and value emotional intimacy. They are supportive partners but may idealize relationships. They need partners who respect their values.",
                "famous_examples": "William Shakespeare, J.R.R. Tolkien, Princess Diana, John Lennon, Audrey Hepburn"
            },
            "INTP": {
                "title": "The Thinker",
                "description": "Innovative inventors with an unquenchable thirst for knowledge. They are logical, analytical, and enjoy theoretical problem-solving above all else.",
                "strengths": "1. Original and inventive\n2. Objective and logical\n3. Open-minded and curious\n4. Honest and straightforward\n5. Independent and self-motivated",
                "growth_areas": "1. Considering emotional impacts\n2. Following through on projects\n3. Developing social skills\n4. Being more decisive\n5. Valuing practical applications",
                "career_suggestions": "1. Theoretical Physics\n2. Mathematics\n3. Computer Science\n4. Philosophy of Science\n5. Engineering\n6. Neuroscience\n7. Artificial Intelligence\n8. Linguistics",
                "relationships": "INTPs value intellectual connection and personal freedom. They may struggle with emotional expression but are loyal partners. They need space for independent thinking.",
                "famous_examples": "Albert Einstein, Charles Darwin, Marie Curie, Abraham Lincoln, Socrates"
            },
            "ESTP": {
                "title": "The Entrepreneur",
                "description": "Smart, energetic, and perceptive people who truly enjoy living on the edge. They are action-oriented problem-solvers who bring immediate energy to any situation.",
                "strengths": "1. Bold and practical\n2. Original and direct\n3. Perceptive and observant\n4. Excellent in crises\n5. Social and spontaneous",
                "growth_areas": "1. Considering long-term consequences\n2. Developing patience\n3. Valuing commitments more\n4. Being more sensitive to others\n5. Planning ahead",
                "career_suggestions": "1. Marketing\n2. Entrepreneurship\n3. Sports Management\n4. Hospitality\n5. Criminal Justice\n6. Emergency Medicine\n7. Construction Management\n8. Real Estate",
                "relationships": "ESTPs are exciting, spontaneous partners who value fun and adventure. They show love through shared experiences. They may struggle with emotional depth and long-term planning.",
                "famous_examples": "Ernest Hemingway, Madonna, Donald Trump, Winston Churchill, Jack Nicholson"
            },
            "ESFP": {
                "title": "The Entertainer",
                "description": "Spontaneous, energetic, and enthusiastic people who love life, people, and material comforts. They are the life of the party and enjoy bringing joy to others.",
                "strengths": "1. Bold and original\n2. Practical and observant\n3. Excellent people skills\n4. Generous and optimistic\n5. Natural performers",
                "growth_areas": "1. Developing follow-through\n2. Considering future consequences\n3. Handling conflict better\n4. Valuing alone time\n5. Setting long-term goals",
                "career_suggestions": "1. Performing Arts\n2. Music\n3. Event Management\n4. Mass Communication\n5. Hospitality\n6. Tourism\n7. Public Relations\n8. Sports Coaching",
                "relationships": "ESFPs are fun-loving, affectionate partners who enjoy shared experiences. They express love through physical affection and acts of service. They may avoid serious conversations.",
                "famous_examples": "Marilyn Monroe, Elvis Presley, Jamie Oliver, Bill Clinton, Adele"
            },
            "ENFP": {
                "title": "The Campaigner",
                "description": "Enthusiastic, creative, and sociable free spirits who can always find a reason to smile. They see life as full of possibilities and connect deeply with others.",
                "strengths": "1. Curious and perceptive\n2. Energetic and enthusiastic\n3. Excellent communicators\n4. Popular and friendly\n5. Empathetic and caring",
                "growth_areas": "1. Developing focus\n2. Following through on projects\n3. Setting boundaries\n4. Handling criticism better\n5. Managing time effectively",
                "career_suggestions": "1. Journalism\n2. Media Studies\n3. Development Studies\n4. Public Relations\n5. Psychology\n6. Counseling\n7. Education\n8. Creative Arts",
                "relationships": "ENFPs seek deep, meaningful connections and value emotional intimacy. They are affectionate partners but may struggle with commitment. They need partners who appreciate their enthusiasm.",
                "famous_examples": "Robin Williams, Walt Disney, Ellen DeGeneres, Robert Downey Jr., Oscar Wilde"
            },
            "ENTP": {
                "title": "The Debater",
                "description": "Smart, curious thinkers who cannot resist an intellectual challenge. They are quick, ingenious, and excellent at reading other people and finding connections.",
                "strengths": "1. Knowledgeable and quick-witted\n2. Original and imaginative\n3. Excellent brainstormers\n4. Charismatic and energetic\n5. Rational and objective",
                "growth_areas": "1. Developing follow-through\n2. Being more sensitive to others\n3. Avoiding unnecessary arguments\n4. Valuing stability more\n5. Practicing patience",
                "career_suggestions": "1. Business Innovation\n2. Political Science\n3. Law\n4. Advertising\n5. Entrepreneurship\n6. Engineering\n7. Economics\n8. Philosophy",
                "relationships": "ENTPs value intellectual stimulation and personal growth in relationships. They enjoy debating but may struggle with emotional expression. They need partners who challenge them.",
                "famous_examples": "Thomas Edison, Benjamin Franklin, Mark Twain, Voltaire, Steve Jobs"
            },
            "ESTJ": {
                "title": "The Executive",
                "description": "Excellent administrators who value tradition, order, and security. They are practical, realistic, and unsurpassed at managing things and people.",
                "strengths": "1. Dedicated and strong-willed\n2. Direct and honest\n3. Loyal and reliable\n4. Excellent organizers\n5. Practical and realistic",
                "growth_areas": "1. Being more open to new ideas\n2. Considering others' feelings\n3. Being more flexible\n4. Valuing innovation more\n5. Delegating effectively",
                "career_suggestions": "1. Business Administration\n2. Finance\n3. Law\n4. Public Administration\n5. Accounting\n6. Military Science\n7. Criminal Justice\n8. Project Management",
                "relationships": "ESTJs are reliable, traditional partners who value stability. They show love through practical support. They may struggle with emotional expression and flexibility.",
                "famous_examples": "Judge Judy, George W. Bush, Frank Sinatra, Lyndon B. Johnson, James Monroe"
            },
            "ESFJ": {
                "title": "The Consul",
                "description": "Caring, social, and popular individuals who are always eager to help. They are practical, warm, and cooperative, valuing harmony and generosity.",
                "strengths": "1. Practical and reliable\n2. Sensitive and caring\n3. Strong social skills\n4. Loyal and hardworking\n5. Excellent organizers",
                "growth_areas": "1. Setting healthier boundaries\n2. Saying no without guilt\n3. Handling criticism better\n4. Being less people-pleasing\n5. Valuing alone time",
                "career_suggestions": "1. Elementary Education\n2. Healthcare Administration\n3. Nursing\n4. Human Resources\n5. Social Work\n6. Counseling\n7. Nutrition/Dietetics\n8. Event Planning",
                "relationships": "ESFJs are nurturing, devoted partners who prioritize their loved ones' needs. They express love through acts of service. They may struggle with conflict and need appreciation.",
                "famous_examples": "Taylor Swift, Bill Gates, Steve Harvey, Dolley Madison, Sally Field"
            },
            "ENFJ": {
                "title": "The Protagonist",
                "description": "Charismatic and inspiring leaders who can motivate others toward growth. They are empathetic, persuasive, and naturally attuned to others' emotions and needs.",
                "strengths": "1. Receptive and reliable\n2. Charismatic and inspiring\n3. Empathetic and caring\n4. Organized and decisive\n5. Natural leaders",
                "growth_areas": "1. Setting healthier boundaries\n2. Avoiding people-pleasing\n3. Handling criticism better\n4. Being less perfectionistic\n5. Valuing alone time",
                "career_suggestions": "1. Psychology\n2. Education\n3. Public Health\n4. Organizational Leadership\n5. Counseling\n6. Human Resources\n7. Public Relations\n8. Social Work",
                "relationships": "ENFJs seek deep, meaningful connections and are highly attentive partners. They may neglect their own needs while caring for others. They value emotional intimacy and growth.",
                "famous_examples": "Barack Obama, Oprah Winfrey, Martin Luther King Jr., John C. Maxwell, Tony Robbins"
            },
            "ENTJ": {
                "title": "The Commander",
                "description": "Bold, imaginative, and strong-willed leaders who always find a way. They are strategic, logical, and excellent at implementing plans and mobilizing people.",
                "strengths": "1. Efficient and energetic\n2. Self-confident and assertive\n3. Strong-willed and decisive\n4. Strategic and logical\n5. Excellent organizers",
                "growth_areas": "1. Being more patient\n2. Considering others' feelings\n3. Delegating effectively\n4. Valuing downtime\n5. Practicing humility",
                "career_suggestions": "1. Strategic Management\n2. Economics\n3. Law\n4. International Business\n5. Political Science\n6. Engineering\n7. Entrepreneurship\n8. Finance",
                "relationships": "ENTJs value intellectual connection and shared goals in relationships. They are loyal but may struggle with emotional expression. They need partners who respect their ambition.",
                "famous_examples": "Margaret Thatcher, Steve Jobs, Franklin D. Roosevelt, Gordon Ramsay, Jim Carrey"
            }
        }
        
    def get_e_score(self):
        """Return E score as percentage (0-100)"""
        total = (self.raw_e_score or 0) + (self.raw_i_score or 0)
        return int((self.raw_e_score / total) * 100) if total else 50

    def get_i_score(self):
        """Return I score as percentage (0-100)"""
        return 100 - self.get_e_score()

    def get_s_score(self):
        """Return S score as percentage (0-100)"""
        total = (self.raw_s_score or 0) + (self.raw_n_score or 0)
        return int((self.raw_s_score / total) * 100) if total else 50

    def get_n_score(self):
        """Return N score as percentage (0-100)"""
        return 100 - self.get_s_score()

    def get_t_score(self):
        """Return T score as percentage (0-100)"""
        total = (self.raw_t_score or 0) + (self.raw_f_score or 0)
        return int((self.raw_t_score / total) * 100) if total else 50

    def get_f_score(self):
        """Return F score as percentage (0-100)"""
        return 100 - self.get_t_score()

    def get_j_score(self):
        """Return J score as percentage (0-100)"""
        total = (self.raw_j_score or 0) + (self.raw_p_score or 0)
        return int((self.raw_j_score / total) * 100) if total else 50

    def get_p_score(self):
        """Return P score as percentage (0-100)"""
        return 100 - self.get_j_score()

    def get_type_description(self):
        """Get description for this personality type"""
        type_data = self.get_type_data().get(self.type_code, {})
        return type_data.get('description', '')

    def get_strengths(self):
        """Get strengths for this personality type"""
        type_data = self.get_type_data().get(self.type_code, {})
        return type_data.get('strengths', '')

    def get_growth_areas(self):
        """Get growth areas for this personality type"""
        type_data = self.get_type_data().get(self.type_code, {})
        return type_data.get('growth_areas', '')

    def get_career_suggestions(self):
        """Get career suggestions for this personality type"""
        type_data = self.get_type_data().get(self.type_code, {})
        return type_data.get('career_suggestions', '')

    def get_relationships(self):
        """Get relationships info for this personality type"""
        type_data = self.get_type_data().get(self.type_code, {})
        return type_data.get('relationships', '')

    def get_famous_examples(self):
        """Get famous examples for this personality type"""
        type_data = self.get_type_data().get(self.type_code, {})
        return type_data.get('famous_examples', '')

    def get_chart_image(self):
        """Generate and return base64 encoded chart image"""
        return generate_personality_chart(self)