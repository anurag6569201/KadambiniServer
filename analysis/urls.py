from django.urls import path

app_name = 'analysis'

urlpatterns = [
    path('generation-insights/', generation_insights.as_view(), name='generation_insights'),
]