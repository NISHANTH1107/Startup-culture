from django.db import migrations

def forwards_func(apps, schema_editor):
    PersonalityResult = apps.get_model('career_site', 'PersonalityResult')
    Assessment = apps.get_model('career_site', 'Assessment')
    
    for result in PersonalityResult.objects.filter(assessment__isnull=True):
        assessment = Assessment.objects.create(
            user=result.assessment.user,  # Adjust if needed
            completed=True
        )
        result.assessment = assessment
        result.save()

class Migration(migrations.Migration):
    dependencies = [
        ('career_site', '0001_initial'),  # Replace with your last migration
    ]
    
    operations = [
        migrations.RunPython(forwards_func),
    ]