from django.utils import timezone
from maintree.models import UserFamilyTree
from analysis.familyData.data_extraction import transform_family_data
from analysis.ai_functions.generations_health_insights_ai import get_health_insights_from_gemini
from analysis.configuration.ai_config import ai_config
from analysis.prompts.generations_health_insights_prompt import generations_health_insights_create_prompt
from maintree.serializers import UserFamilyTreeSerializer
from .models import GenerationalInsights,HereditaryRiskInsights
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from analysis.ai_functions.hereditary_risk_insights_ai import get_hereditary_risk_insights_prompt_from_gemini
from analysis.prompts.hereditary_risk_insights_prompt import get_hereditary_risk_insights_create_prompt

class get_family_data_requested_user(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # 1. fetch or create the family tree
        tree, _ = UserFamilyTree.objects.get_or_create(user=request.user)

        # 2. fetch or create the cached insights
        insights, created = GenerationalInsights.objects.get_or_create(user=request.user)

        # 3. if it's brand new, OR the tree was modified since we last ran…
        if created or tree.last_modified > insights.last_generated:
            # a) transform, prompt and call the model
            raw = {
                **UserFamilyTreeSerializer(tree).data
            }
            transformed = transform_family_data(raw)

            ai_model = ai_config()
            prompt = get_hereditary_risk_insights_create_prompt(transformed)
            result = get_health_insights_from_gemini(ai_model, prompt)

            # b) save back into our cache
            insights.ai_response_data = result
            insights.save()  # this also updates last_generated

        # 4. return whatever is on file
        return Response(insights.ai_response_data, status=status.HTTP_200_OK)



class get_hereditary_risk_insights_user(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # 1. fetch or create the family tree
        tree, _ = UserFamilyTree.objects.get_or_create(user=request.user)

        # 2. fetch or create the cached insights
        insights, created = HereditaryRiskInsights.objects.get_or_create(user=request.user)

        # 3. if it's brand new, OR the tree was modified since we last ran…
        if created or tree.last_modified > insights.last_generated:
            # a) transform, prompt and call the model
            raw = {
                **UserFamilyTreeSerializer(tree).data
            }
            transformed = transform_family_data(raw)

            ai_model = ai_config()
            prompt = get_hereditary_risk_insights_create_prompt(transformed)
            result = get_hereditary_risk_insights_prompt_from_gemini(ai_model, prompt)

            # b) save back into our cache
            insights.ai_response_data = result
            insights.save()  # this also updates last_generated

        # 4. return whatever is on file
        return Response(insights.ai_response_data, status=status.HTTP_200_OK)
