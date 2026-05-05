from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from ckeditor.fields import RichTextField

DIFFICULTY_CHOICES = [
    ('easy', 'سهل / Easy'),
    ('medium', 'متوسط / Medium'),
    ('hard', 'صعب / Hard'),
]

POINTS_MAP = {'easy': 10, 'medium': 20, 'hard': 30}

LEVEL_THRESHOLDS = [
    (0,    1, 'مبتدئ',     'Beginner'),
    (100,  2, 'متوسط',     'Intermediate'),
    (250,  3, 'متقدم',     'Advanced'),
    (500,  4, 'خبير',      'Expert'),
    (1000, 5, 'محترف',     'Master'),
]


class ScamType(models.Model):
    title_ar = models.CharField(max_length=200, verbose_name="العنوان (عربي)")
    description_ar = models.TextField(verbose_name="وصف مختصر (عربي)")
    details_ar = RichTextField(verbose_name="التفاصيل (عربي)", default="")

    title_en = models.CharField(max_length=200, verbose_name="Title (English)", default="")
    description_en = models.TextField(verbose_name="Short Description (English)", default="")
    details_en = RichTextField(verbose_name="Details (English)", default="")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title_ar


class PhishingScenario(models.Model):
    title_ar = models.CharField(max_length=200, verbose_name="عنوان الرسالة (عربي)")
    title_en = models.CharField(max_length=200, verbose_name="Title (English)")
    image = models.ImageField(upload_to='phishing_scenarios/', verbose_name="صورة الرسالة", blank=True, null=True)
    is_scam = models.BooleanField(default=True, verbose_name="هل هي احتيال؟ (نعم = صح)")
    difficulty = models.CharField(
        max_length=10, choices=DIFFICULTY_CHOICES, default='medium',
        verbose_name="مستوى الصعوبة / Difficulty"
    )
    explanation_ar = models.TextField(verbose_name="التفسير بالعربي")
    explanation_en = models.TextField(verbose_name="Explanation in English")

    def __str__(self):
        return self.title_ar


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    points = models.IntegerField(default=0)

    @property
    def level_info(self):
        current = LEVEL_THRESHOLDS[0]
        for threshold in LEVEL_THRESHOLDS:
            if self.points >= threshold[0]:
                current = threshold
        return current

    @property
    def level(self):
        return self.level_info[1]

    @property
    def level_name_ar(self):
        return self.level_info[2]

    @property
    def level_name_en(self):
        return self.level_info[3]

    @property
    def level_progress_pct(self):
        idx = self.level - 1
        current_pts = LEVEL_THRESHOLDS[idx][0]
        if idx + 1 < len(LEVEL_THRESHOLDS):
            next_pts = LEVEL_THRESHOLDS[idx + 1][0]
            return min(100, round((self.points - current_pts) / (next_pts - current_pts) * 100))
        return 100

    @property
    def points_to_next_level(self):
        idx = self.level - 1
        if idx + 1 < len(LEVEL_THRESHOLDS):
            return LEVEL_THRESHOLDS[idx + 1][0] - self.points
        return 0

    def __str__(self):
        return f"{self.user.username} — {self.points} pts"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    UserProfile.objects.get_or_create(user=instance)


class UserAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempts')
    scenario = models.ForeignKey(PhishingScenario, on_delete=models.CASCADE)
    was_correct = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class ScenarioReport(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    submitted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='submitted_reports', verbose_name="Submitted By"
    )
    language = models.CharField(
        max_length=2, choices=[('ar', 'Arabic'), ('en', 'English')],
        verbose_name="Submission Language"
    )
    title = models.CharField(max_length=200, verbose_name="Title (in submission language)")
    image = models.ImageField(
        upload_to='reported_scenarios/', blank=True, null=True,
        verbose_name="Screenshot / Image (optional)"
    )
    is_scam = models.BooleanField(default=True, verbose_name="Is this a phishing/scam attempt?")
    explanation = models.TextField(verbose_name="Explanation (in submission language)")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    # Admin fills these when approving
    difficulty = models.CharField(
        max_length=10, choices=DIFFICULTY_CHOICES, blank=True,
        verbose_name="Difficulty (admin sets)"
    )
    title_translated = models.CharField(
        max_length=200, blank=True,
        verbose_name="Title in other language (admin translates)"
    )
    explanation_translated = models.TextField(
        blank=True,
        verbose_name="Explanation in other language (admin translates)"
    )
    rejection_reason = models.TextField(blank=True, verbose_name="Rejection Reason")

    # Link to the created scenario (set after approval)
    created_scenario = models.OneToOneField(
        PhishingScenario, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='source_report', verbose_name="Created Scenario"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reviewed_reports', verbose_name="Reviewed By"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Scenario Report"
        verbose_name_plural = "Scenario Reports"

    def __str__(self):
        return f"[{self.get_status_display()}] {self.title[:60]}"


class SiteWarning(models.Model):
    text_ar = models.TextField(verbose_name="نص التحذير (عربي)")
    text_en = models.TextField(verbose_name="Warning Text (English)")
    is_active = models.BooleanField(default=True, verbose_name="نشط / Active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Site Warning"
        verbose_name_plural = "Site Warnings"

    def __str__(self):
        return self.text_ar[:80]
