from django.urls import path
from .views import get_family_data_requested_user,get_hereditary_risk_insights_user,get_offspring_insights_user,get_pathways_insights_user,get_health_will_wisdom_insights_user,ChatWithGuardianAPIView

app_name = 'analysis'

urlpatterns = [
    path('generate-insights/', get_family_data_requested_user.as_view(), name='generate_health_insights'),
    path('generate-hereditary-insights/', get_hereditary_risk_insights_user.as_view(), name='get_hereditary_risk_insights_user'),
    path('generate-offspring/', get_offspring_insights_user.as_view(), name='get_offspring_insights_user'),
    path('generate-pathways/', get_pathways_insights_user.as_view(), name='get_pathways_insights_user'),

    path('generate-health-wisdom/', get_health_will_wisdom_insights_user.as_view(), name='get_health_will_wisdom_insights_user'),
    path('guardian-chat/', ChatWithGuardianAPIView.as_view(), name='guardian_chat_api'),
]

