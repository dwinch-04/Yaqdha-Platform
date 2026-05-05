from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_phishingscenario_difficulty_userattempt_userprofile'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Make PhishingScenario.image optional
        migrations.AlterField(
            model_name='phishingscenario',
            name='image',
            field=models.ImageField(
                blank=True, null=True,
                upload_to='phishing_scenarios/',
                verbose_name='صورة الرسالة'
            ),
        ),

        # Create ScenarioReport
        migrations.CreateModel(
            name='ScenarioReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(
                    choices=[('ar', 'Arabic'), ('en', 'English')],
                    max_length=2,
                    verbose_name='Submission Language'
                )),
                ('title', models.CharField(max_length=200, verbose_name='Title (in submission language)')),
                ('image', models.ImageField(
                    blank=True, null=True,
                    upload_to='reported_scenarios/',
                    verbose_name='Screenshot / Image (optional)'
                )),
                ('is_scam', models.BooleanField(default=True, verbose_name='Is this a phishing/scam attempt?')),
                ('explanation', models.TextField(verbose_name='Explanation (in submission language)')),
                ('status', models.CharField(
                    choices=[('pending', 'Pending Review'), ('approved', 'Approved'), ('rejected', 'Rejected')],
                    default='pending',
                    max_length=10
                )),
                ('difficulty', models.CharField(
                    blank=True,
                    choices=[('easy', 'سهل / Easy'), ('medium', 'متوسط / Medium'), ('hard', 'صعب / Hard')],
                    max_length=10,
                    verbose_name='Difficulty (admin sets)'
                )),
                ('title_translated', models.CharField(
                    blank=True, max_length=200,
                    verbose_name='Title in other language (admin translates)'
                )),
                ('explanation_translated', models.TextField(
                    blank=True,
                    verbose_name='Explanation in other language (admin translates)'
                )),
                ('rejection_reason', models.TextField(blank=True, verbose_name='Rejection Reason')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('submitted_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='submitted_reports',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Submitted By'
                )),
                ('reviewed_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='reviewed_reports',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Reviewed By'
                )),
                ('created_scenario', models.OneToOneField(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='source_report',
                    to='main.phishingscenario',
                    verbose_name='Created Scenario'
                )),
            ],
            options={
                'verbose_name': 'Scenario Report',
                'verbose_name_plural': 'Scenario Reports',
                'ordering': ['-created_at'],
            },
        ),
    ]
