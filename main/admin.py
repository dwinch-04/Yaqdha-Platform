from django.contrib import admin
from .models import ScamType

admin.site.register(ScamType)

from .models import PhishingScenario

admin.site.register(PhishingScenario)