
from django.core.management.base import BaseCommand
from career_site.models import CareerLibrary, CareerCategory, CareerSubCategory, TopInstitute
import random
from faker import Faker

fake = Faker()

# Career demand profiles (current, long-term, very-long-term)
DEMAND_PROFILES = {
    # (Current, 5-year, 10-year)
    'booming': (7, 6, 5),       # Currently peaking, then normalizing
    'growing': (5, 6, 7),       # Steady growth
    'stable': (5, 5, 5),        # Consistent demand
    'declining': (4, 3, 2),     # Gradual decline
    'volatile': (6, 4, 7),      # Unpredictable changes
    'niche': (3, 4, 4),         # Small but stable
}

CAREER_TYPES = {
    'Engineering': [
        ('AI Engineer', 'growing'),
        ('Robotics Engineer', 'growing'),
        ('Civil Engineer', 'stable'),
        ('Petroleum Engineer', 'declining'),
        ('Renewable Energy Engineer', 'booming'),
        ('Biomedical Engineer', 'growing'),
        ('Automotive Engineer', 'volatile'),
        ('Quantum Computing Engineer', 'booming'),
        ('Cybersecurity Engineer', 'booming'),
        ('Nanotechnology Engineer', 'growing')
    ],
    'Medical': [
        ('Telemedicine Specialist', 'booming'),
        ('Genetic Counselor', 'growing'),
        ('Robotic Surgeon', 'growing'),
        ('Epidemiologist', 'volatile'),
        ('Geriatric Care Specialist', 'growing'),
        ('Neuroscientist', 'stable'),
        ('Sports Medicine Physician', 'stable'),
        ('Medical AI Developer', 'booming'),
        ('Cancer Researcher', 'stable'),
        ('Rural Healthcare Provider', 'niche')
    ],
    # Add more career types as needed
}

class Command(BaseCommand):
    help = 'Populates the database with mock career data with meaningful demand trends'

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating mock career data with demand profiles...")
        
        # Create Career Libraries
        libraries = [
            CareerLibrary.objects.create(
                title=f"{field} Career Library",
                description=fake.paragraph(nb_sentences=5),
            ) for field in ['Engineering', 'Medical', 'Technology', 'Business', 
                           'Creative Arts', 'Science', 'Education', 
                           'Healthcare', 'Government', 'Environmental']
        ]

        # Create Categories and SubCategories with meaningful demand data
        for library in libraries:
            field = library.title.split()[0].lower()
            
            for i in range(10):  # 10 categories per library
                category = CareerCategory.objects.create(
                    library=library,
                    name=f"{fake.word().title()} {library.title.split()[0]} Careers",
                    description=fake.paragraph(nb_sentences=3),
                    card_count=10
                )

                # Get appropriate career types for this field
                careers = CAREER_TYPES.get(library.title.split()[0], [])
                if not careers:
                    careers = [(f"{fake.job()} Specialist", random.choice(list(DEMAND_PROFILES.keys()))) 
                              for _ in range(10)]

                for career_name, demand_profile in careers[:10]:  # 10 subcategories
                    demand = DEMAND_PROFILES[demand_profile]
                    
                    subcategory = CareerSubCategory.objects.create(
                        category=category,
                        name=career_name,
                        summary=self.generate_career_summary(career_name),
                        daily_tasks=self.generate_daily_tasks(career_name),
                        current_demand=demand[0],
                        long_term_demand=demand[1],
                        very_long_term_demand=demand[2]
                    )

                    # Create 10 institutes for each subcategory
                    for _ in range(10):
                        TopInstitute.objects.create(
                            career=subcategory,
                            name=f"{fake.company()} {random.choice(['University', 'Institute', 'College'])}",
                            location=fake.city(),
                            is_private=random.choice([True, False]),
                            rating=round(random.uniform(3, 5), 1)
                        )

        self.stdout.write(self.style.SUCCESS("Successfully populated database with realistic career data!"))

    def generate_career_summary(self, career_name):
        summaries = {
            'AI Engineer': "Develop cutting-edge artificial intelligence systems that transform industries. "
                          "Requires expertise in machine learning, neural networks, and data analysis.",
            'Robotics Engineer': "Design and build robotic systems for manufacturing, healthcare, and exploration. "
                               "Combines mechanical, electrical, and software engineering skills.",
            # Add more specific summaries
        }
        return summaries.get(career_name, fake.paragraph(nb_sentences=5))

    def generate_daily_tasks(self, career_name):
        tasks = {
            'AI Engineer': [
                "Develop and train machine learning models",
                "Clean and preprocess large datasets",
                "Optimize neural network architectures",
                "Collaborate with product teams on AI integration",
                "Research latest AI publications"
            ],
            'Robotics Engineer': [
                "Design robotic system components",
                "Program robot control systems",
                "Test prototypes in simulated environments",
                "Troubleshoot mechanical/electrical issues",
                "Document design specifications"
            ],
            # Add more specific tasks
        }
        return "\n".join(tasks.get(career_name, 
            [fake.sentence() for _ in range(5)]))