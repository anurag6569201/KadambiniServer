from django.utils import timezone
from maintree.models import UserFamilyTree
from analysis.familyData.data_extraction import transform_family_data
from analysis.ai_functions.generations_health_insights_ai import get_health_insights_from_gemini
from analysis.configuration.ai_config import ai_config
from analysis.prompts.generations_health_insights_prompt import generations_health_insights_create_prompt
from maintree.serializers import UserFamilyTreeSerializer
from .models import GenerationalInsights,HereditaryRiskInsights,PathwaysRiskInsights,OffspringsRiskInsights
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from analysis.ai_functions.hereditary_risk_insights_ai import get_hereditary_risk_insights_prompt_from_gemini
from analysis.prompts.hereditary_risk_insights_prompt import get_hereditary_risk_insights_create_prompt

from analysis.ai_functions.offspring_risk_insights_ai import get_offspringrisk_insights_prompt_from_gemini
from analysis.prompts.offspring_health_insights_prompt import offspring_health_insights_prompt

from analysis.ai_functions.pathways_risk_insights_ai import get_pathways_risk_insights_prompt_from_gemini
from analysis.prompts.pathways_health_insights_prompt import pathways_health_insights_prompt


class get_family_data_requested_user(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        tree, _ = UserFamilyTree.objects.get_or_create(user=request.user)
        insights, created = GenerationalInsights.objects.get_or_create(user=request.user)
        if created or tree.last_modified > insights.last_generated:
            raw = {
                **UserFamilyTreeSerializer(tree).data
            }
            transformed = transform_family_data(raw)
            ai_model = ai_config()
            prompt = generations_health_insights_create_prompt(transformed)
            result = get_health_insights_from_gemini(ai_model, prompt)
            insights.ai_response_data = result
            insights.save()  

        return Response(insights.ai_response_data, status=status.HTTP_200_OK)



class get_hereditary_risk_insights_user(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        tree, _ = UserFamilyTree.objects.get_or_create(user=request.user)
        insights, created = HereditaryRiskInsights.objects.get_or_create(user=request.user)
        if created or tree.last_modified > insights.last_generated:
            raw = {
                **UserFamilyTreeSerializer(tree).data
            }
            transformed = transform_family_data(raw)

            ai_model = ai_config()
            prompt = get_hereditary_risk_insights_create_prompt(transformed)
            result = get_hereditary_risk_insights_prompt_from_gemini(ai_model, prompt)
            insights.ai_response_data = result
            insights.save() 

        return Response(insights.ai_response_data, status=status.HTTP_200_OK)



class get_offspring_insights_user(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        tree, _ = UserFamilyTree.objects.get_or_create(user=request.user)
        insights, created = OffspringsRiskInsights.objects.get_or_create(user=request.user)
        if created or tree.last_modified > insights.last_generated:
            raw = {
                **UserFamilyTreeSerializer(tree).data
            }
            transformed = transform_family_data(raw)

            ai_model = ai_config()
            prompt = offspring_health_insights_prompt(transformed)
            result = get_offspringrisk_insights_prompt_from_gemini(ai_model, prompt)
            insights.ai_response_data = result
            insights.save() 

        return Response(insights.ai_response_data, status=status.HTTP_200_OK)



class get_pathways_insights_user(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        tree, _ = UserFamilyTree.objects.get_or_create(user=request.user)
        insights, created = PathwaysRiskInsights.objects.get_or_create(user=request.user)
        if created or tree.last_modified > insights.last_generated:
            raw = {
                **UserFamilyTreeSerializer(tree).data
            }
            transformed = transform_family_data(raw)

            ai_model = ai_config()
            prompt = pathways_health_insights_prompt(transformed)
            result = get_pathways_risk_insights_prompt_from_gemini(ai_model, prompt)
            insights.ai_response_data = result
            insights.save() 

        return Response(insights.ai_response_data, status=status.HTTP_200_OK)
