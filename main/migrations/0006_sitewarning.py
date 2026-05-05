from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_scenarioreport_phishingscenario_image_optional'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteWarning',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_ar', models.TextField(verbose_name='نص التحذير (عربي)')),
                ('text_en', models.TextField(verbose_name='Warning Text (English)')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط / Active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Site Warning',
                'verbose_name_plural': 'Site Warnings',
            },
        ),
    ]
