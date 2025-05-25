from django.urls import path
from .views import get_family_data_requested_user

app_name = 'analysis'

urlpatterns = [
    path('generate-insights/', get_family_data_requested_user.as_view(), name='generate_health_insights'),
]