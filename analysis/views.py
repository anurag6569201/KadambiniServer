import datetime
import uuid
from django.utils import timezone
from maintree.models import UserFamilyTree
from analysis.familyData.data_extraction import transform_family_data
from analysis.ai_functions.generations_health_insights_ai import get_health_insights_from_gemini
from analysis.configuration.ai_config import ai_config
from analysis.prompts.generations_health_insights_prompt import generations_health_insights_create_prompt
from maintree.serializers import UserFamilyTreeSerializer
from .models import GenerationalInsights,HereditaryRiskInsights,PathwaysRiskInsights,OffspringsRiskInsights,HealthWillWisdomInsights
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from analysis.ai_functions.hereditary_risk_insights_ai import get_hereditary_risk_insights_prompt_from_gemini
from analysis.prompts.hereditary_risk_insights_prompt import get_hereditary_risk_insights_create_prompt

from analysis.ai_functions.offspring_risk_insights_ai import get_offspringrisk_insights_prompt_from_gemini
from analysis.prompts.offspring_health_insights_prompt import offspring_health_insights_prompt

from analysis.ai_functions.pathways_risk_insights_ai import get_pathways_risk_insights_prompt_from_gemini
from analysis.prompts.pathways_health_insights_prompt import pathways_health_insights_prompt

from analysis.ai_functions.health_will_wisdom_risk_insights_ai import get_health_will_wisdom_insights_prompt_from_gemini
from analysis.prompts.health_will_wisdom_insights_prompt import health_will_and_wisdom_prompt

from analysis.ai_functions.family_health_guardian_ai import family_health_guardian_from_gemini
from analysis.prompts.family_health_guardian_prompt import family_health_guardian_prompt


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



class get_health_will_wisdom_insights_user(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        tree, _ = UserFamilyTree.objects.get_or_create(user=request.user)
        insights, created = HealthWillWisdomInsights.objects.get_or_create(user=request.user)
        if created or tree.last_modified > insights.last_generated:
            raw = {
                **UserFamilyTreeSerializer(tree).data
            }
            transformed = transform_family_data(raw)

            ai_model = ai_config()
            prompt = health_will_and_wisdom_prompt(transformed)
            result = get_health_will_wisdom_insights_prompt_from_gemini(ai_model, prompt)
            insights.ai_response_data = result
            insights.save() 

        return Response(insights.ai_response_data, status=status.HTTP_200_OK)


class ChatWithGuardianAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated] 

    def post(self, request, *args, **kwargs):
        tree, _ = UserFamilyTree.objects.get_or_create(user=request.user)
        raw = {
            **UserFamilyTreeSerializer(tree).data
        }
        transformed = transform_family_data(raw)

        user_message_content = request.data.get('message', '').strip()
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
            
        print(f"Session ID: {session_id}")


        if not user_message_content:
            return Response(
                {"error": "Message content cannot be empty."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Manage conversation history in session
        conversation_history = request.session.get('conversation_history', [])
        
        # Add user message to history
        conversation_history.append({"role": "user", "content": user_message_content})
        
        # Limit history size to avoid overly long prompts (e.g., last N turns)
        max_history_turns = 3
        if len(conversation_history) > max_history_turns * 2:
            conversation_history = conversation_history[-(max_history_turns * 2):]

        try:
            ai_model = ai_config() 
            prompt = family_health_guardian_prompt(transformed, conversation_history, user_message_content)
            
            gemini_response_data = family_health_guardian_from_gemini(ai_model, prompt)

            if "error" in gemini_response_data:
                ai_reply_content = gemini_response_data.get("raw_response") or "Sorry, I encountered an issue processing your request with the AI. Please try again."
                print(f"Gemini API Error for session {session_id}: {gemini_response_data['error']}")
            else:
                ai_reply_content = gemini_response_data.get("reply", "I'm not sure how to respond to that. Can you try asking differently?")

        except ValueError as ve: 
            print(f"Configuration Error: {ve}")
            return Response({"error": str(ve)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print(f"Error during AI processing: {e}")
            ai_reply_content = "An unexpected error occurred while I was thinking. Please try again."

        # Add AI response to history
        conversation_history.append({"role": "assistant", "content": ai_reply_content})
        request.session['conversation_history'] = conversation_history 

        current_utc_time = datetime.datetime.now(datetime.timezone.utc)
        formatted_timestamp = current_utc_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        ai_response_payload = {
            'id': str(uuid.uuid4()),
            'content': ai_reply_content,
            'sender': 'ai',
            'timestamp': formatted_timestamp 
        }
        
        return Response(ai_response_payload, status=status.HTTP_200_OK)
