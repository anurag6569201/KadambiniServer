from django.db import models
from django.conf import settings

class GenerationalInsights(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='generation_health_insight_user'
    )
    ai_response_data = models.JSONField(default=list)
    last_generated = models.DateTimeField(auto_now=True)  # new!
    
    def __str__(self):
        return f"Generation Health Insight for {self.user.username}"


class HereditaryRiskInsights(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='generation_hereditary_insight_user'
    )
    ai_response_data = models.JSONField(default=list)
    last_generated = models.DateTimeField(auto_now=True)  # new!
    
    def __str__(self):
        return f"Hereditary Health Insight for {self.user.username}"



class OffspringsRiskInsights(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='generation_offsprings_insight_user'
    )
    ai_response_data = models.JSONField(default=list)
    last_generated = models.DateTimeField(auto_now=True)  # new!
    
    def __str__(self):
        return f"Offspring Health Insight for {self.user.username}"



class PathwaysRiskInsights(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='generation_pathways_insight_user'
    )
    ai_response_data = models.JSONField(default=list)
    last_generated = models.DateTimeField(auto_now=True)  # new!
    
    def __str__(self):
        return f"Pathways Health Insight for {self.user.username}"




class HealthWillWisdomInsights(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='generation_health_will_wisdom_insight_user'
    )
    ai_response_data = models.JSONField(default=list)
    last_generated = models.DateTimeField(auto_now=True)  # new!
    
    def __str__(self):
        return f"Health Will Wisdom Insight for {self.user.username}"

