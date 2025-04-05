from django.core.management.base import BaseCommand
from career_site.models import MasterClassCategory, MasterClassVideo

class Command(BaseCommand):
    help = 'Populates the database with Master Class categories and videos'

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating Master Class data...")
        
        # Clear existing data
        MasterClassCategory.objects.all().delete()
        
        # Create categories and videos
        categories_data = [
            {
                "title": "Medical Science",
                "description": "Comprehensive courses for medical students and professionals",
                "videos": [
                    {
                        "title": "Introduction to NEET",
                        "youtube_id": "Yb4W9_JU6eE",
                        "description": "Everything you need to know about NEET examination",
                        "duration": "15:30"
                    },
                    {
                        "title": "MBBS Abroad Guide",
                        "youtube_id": "KtW7Hhmep2Q",
                        "description": "Complete guide to pursuing MBBS in foreign countries",
                        "duration": "22:15"
                    },
                    {
                        "title": "Medical Career Paths",
                        "youtube_id": "9Z1KWmTTX1I",
                        "description": "Exploring different career options after MBBS",
                        "duration": "18:45"
                    }
                ]
            },
            {
                "title": "AYUSH - Alternate Medicine",
                "description": "Courses on Ayurveda, Yoga, Unani, Siddha, and Homeopathy",
                "videos": [
                    {
                        "title": "Introduction to Ayurveda",
                        "youtube_id": "gZ5bFkwB0UU",
                        "description": "Fundamentals of Ayurvedic medicine",
                        "duration": "12:20"
                    },
                    {
                        "title": "Yoga for Beginners",
                        "youtube_id": "v7AYKMP6rOE",
                        "description": "Basic yoga asanas for daily practice",
                        "duration": "25:00"
                    }
                ]
            },
            {
                "title": "Engineering Careers",
                "description": "Master classes for engineering students",
                "videos": [
                    {
                        "title": "Future of AI Engineering",
                        "youtube_id": "JMUxmLyrhSk",
                        "description": "Emerging trends in artificial intelligence",
                        "duration": "20:10"
                    },
                    {
                        "title": "Robotics Fundamentals",
                        "youtube_id": "0X5zw4G_6Wo",
                        "description": "Introduction to robotics engineering",
                        "duration": "17:35"
                    }
                ]
            }
        ]

        for idx, category_data in enumerate(categories_data, start=1):
            category = MasterClassCategory.objects.create(
                title=category_data['title'],
                description=category_data['description'],
                order=idx
            )
            
            for video_idx, video_data in enumerate(category_data['videos'], start=1):
                MasterClassVideo.objects.create(
                    category=category,
                    title=video_data['title'],
                    youtube_id=video_data['youtube_id'],
                    description=video_data['description'],
                    duration=video_data['duration'],
                    order=video_idx
                )
            
            self.stdout.write(f"Created category: {category.title} with {len(category_data['videos'])} videos")


        self.stdout.write(self.style.SUCCESS("Successfully populated Master Class data!"))