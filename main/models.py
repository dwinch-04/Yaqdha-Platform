from django.db import models
from ckeditor.fields import RichTextField 

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
    image = models.ImageField(upload_to='phishing_scenarios/', verbose_name="صورة الرسالة")
    is_scam = models.BooleanField(default=True, verbose_name="هل هي احتيال؟ (نعم = صح)")
    

    explanation_ar = models.TextField(verbose_name="التفسير بالعربي")
    explanation_en = models.TextField(verbose_name="Explanation in English")

    def __str__(self):
        return self.title_ar