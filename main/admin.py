from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import ScamType, PhishingScenario, UserProfile, UserAttempt, ScenarioReport, SiteWarning


admin.site.register(ScamType)
admin.site.register(PhishingScenario)
admin.site.register(UserProfile)
admin.site.register(UserAttempt)
admin.site.register(SiteWarning)


@admin.register(ScenarioReport)
class ScenarioReportAdmin(admin.ModelAdmin):
    list_display = ('title_short', 'language', 'submitted_by', 'is_scam', 'status', 'created_at', 'scenario_link')
    list_filter  = ('status', 'language', 'is_scam')
    search_fields = ('title', 'submitted_by__username')
    readonly_fields = ('submitted_by', 'language', 'title', 'is_scam', 'explanation',
                       'image_preview', 'created_at', 'reviewed_by', 'reviewed_at', 'created_scenario')

    fieldsets = (
        ('Submission (read-only)', {
            'fields': ('submitted_by', 'language', 'title', 'is_scam', 'explanation', 'image_preview', 'created_at')
        }),
        ('Admin Review', {
            'description': (
                'To approve: set Status → Approved, fill Difficulty and both translation fields, then Save. '
                'A PhishingScenario will be created automatically. '
                'To reject: set Status → Rejected and optionally fill Rejection Reason.'
            ),
            'fields': ('status', 'difficulty', 'title_translated', 'explanation_translated', 'rejection_reason')
        }),
        ('Outcome', {
            'classes': ('collapse',),
            'fields': ('reviewed_by', 'reviewed_at', 'created_scenario')
        }),
    )

    def title_short(self, obj):
        return obj.title[:60]
    title_short.short_description = 'Title'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:200px;border-radius:8px;">', obj.image.url)
        return '—'
    image_preview.short_description = 'Image Preview'

    def scenario_link(self, obj):
        if obj.created_scenario_id:
            return format_html('<a href="/admin/main/phishingscenario/{}/change/">View</a>', obj.created_scenario_id)
        return '—'
    scenario_link.short_description = 'Scenario'

    def save_model(self, request, obj, form, change):
        is_new_approval = (
            obj.status == 'approved' and
            obj.difficulty and
            obj.title_translated.strip() and
            obj.explanation_translated.strip() and
            obj.created_scenario_id is None
        )

        if is_new_approval:
            if obj.language == 'ar':
                title_ar, title_en = obj.title, obj.title_translated
                exp_ar, exp_en    = obj.explanation, obj.explanation_translated
            else:
                title_en, title_ar = obj.title, obj.title_translated
                exp_en, exp_ar    = obj.explanation, obj.explanation_translated

            scenario = PhishingScenario(
                title_ar=title_ar,
                title_en=title_en,
                is_scam=obj.is_scam,
                difficulty=obj.difficulty,
                explanation_ar=exp_ar,
                explanation_en=exp_en,
            )
            if obj.image:
                scenario.image = obj.image
            scenario.save()

            obj.created_scenario = scenario
            obj.reviewed_by  = request.user
            obj.reviewed_at  = timezone.now()

        elif obj.status in ('approved', 'rejected') and not obj.reviewed_at:
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()

        super().save_model(request, obj, form, change)
