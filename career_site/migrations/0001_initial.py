import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_student', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('phone', models.CharField(blank=True, max_length=15)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='CareerLibrary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='career_library/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='MasterClassCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'Master Class Categories',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('option_a', models.CharField(max_length=200)),
                ('option_b', models.CharField(max_length=200)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='AdminProfile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('position', models.CharField(max_length=100)),
                ('department', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='StudentProfile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('education_level', models.CharField(max_length=100)),
                ('interests', models.TextField()),
                ('skills', models.TextField()),
                ('career_goals', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_taken', models.DateTimeField(auto_now_add=True)),
                ('completed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CareerCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='career_categories/')),
                ('card_count', models.PositiveIntegerField(default=0)),
                ('library', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='career_site.careerlibrary')),
            ],
        ),
        migrations.CreateModel(
            name='CareerSubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('summary', models.TextField()),
                ('daily_tasks', models.TextField(help_text='Bullet points separated by newlines')),
                ('image', models.ImageField(blank=True, null=True, upload_to='career_subcategories/')),
                ('current_demand', models.IntegerField(help_text='1=Extremely Low, 7=Extremely High', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(7)])),
                ('long_term_demand', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(7)])),
                ('very_long_term_demand', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(7)])),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='career_site.careercategory')),
            ],
        ),
        migrations.CreateModel(
            name='MasterClassVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('youtube_id', models.CharField(help_text='YouTube video ID (11 characters)', max_length=20)),
                ('description', models.TextField(blank=True)),
                ('duration', models.CharField(blank=True, max_length=20)),
                ('order', models.PositiveIntegerField(default=0)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='career_site.masterclasscategory')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='PersonalityResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('personality_type', models.CharField(max_length=4)),
                ('ei_score', models.IntegerField()),
                ('sn_score', models.IntegerField()),
                ('tf_score', models.IntegerField()),
                ('jp_score', models.IntegerField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('assessment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='result', to='career_site.assessment')),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice', models.BooleanField()),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='career_site.assessment')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='career_site.question')),
            ],
        ),
        migrations.CreateModel(
            name='TopInstitute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('location', models.CharField(max_length=100)),
                ('is_private', models.BooleanField(default=True)),
                ('rating', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('career', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='institutes', to='career_site.careersubcategory')),
            ],
        ),
    ]
