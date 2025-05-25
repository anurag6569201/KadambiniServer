from django.shortcuts import render
from maintree.models import UserFamilyTree
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from maintree.serializers import UserFamilyTreeSerializer
from analysis.familyData.data_extraction import transform_family_data
from analysis.ai_functions.generations_health_insights_ai import get_health_insights_from_gemini
from analysis.configuration.ai_config import ai_config
from analysis.prompts.generations_health_insights_prompt import generations_health_insights_create_prompt

class get_family_data_requested_user(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        instance, created = UserFamilyTree.objects.get_or_create(user=request.user)
        serializer = UserFamilyTreeSerializer(instance)
        
        # Pass serializer.data (Python dict) directly to the transformation function
        transformed_data_dict = transform_family_data(serializer.data)

        # init ai configurations
        ai_model = ai_config()

        # creating prompts
        generations_health_insights_prompt_text = generations_health_insights_create_prompt(transformed_data_dict)

        # calling gemini
        insight_data = get_health_insights_from_gemini(ai_model,generations_health_insights_prompt_text)
        print(insight_data)
        
        return Response(transformed_data_dict, status=status.HTTP_200_OK)
    
