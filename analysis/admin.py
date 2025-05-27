from django.contrib import admin
from analysis.models import HereditaryRiskInsights,GenerationalInsights,OffspringsRiskInsights,PathwaysRiskInsights,HealthWillWisdomInsights


# Register your models here.
admin.site.register(GenerationalInsights)
admin.site.register(HereditaryRiskInsights)
admin.site.register(OffspringsRiskInsights)
admin.site.register(PathwaysRiskInsights)
admin.site.register(HealthWillWisdomInsights)