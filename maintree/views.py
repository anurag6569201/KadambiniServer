# familytree/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import UserFamilyTree
from .serializers import UserFamilyTreeSerializer
from .utils import get_default_family_tree_data
from rest_framework.exceptions import ParseError, ValidationError as DRFValidationError
from pydantic import ValidationError as PydanticValidationError

import json
class UserFamilyTreeView(generics.GenericAPIView):
    serializer_class = UserFamilyTreeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, create_default_if_none=False):
        try:
            tree = UserFamilyTree.objects.get(user=self.request.user)
            if not tree.nodes_data and not tree.edges_data and create_default_if_none:
                default_data = get_default_family_tree_data(user=self.request.user) # Pass user
                tree.nodes_data = default_data['nodes_data']
                tree.edges_data = default_data['edges_data']
            return tree
        except UserFamilyTree.DoesNotExist:
            if create_default_if_none:
                default_data = get_default_family_tree_data(user=self.request.user) # Pass user
                return UserFamilyTree(
                    user=self.request.user,
                    nodes_data=default_data['nodes_data'],
                    edges_data=default_data['edges_data']
                )
            return UserFamilyTree(user=self.request.user, nodes_data=[], edges_data=[])


    def get(self, request, *args, **kwargs):
        instance = self.get_object(create_default_if_none=True)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        instance, created = UserFamilyTree.objects.get_or_create(user=request.user)
        
        if created and not request.data.get('nodes') and not request.data.get('edges'):
            default_data = get_default_family_tree_data(user=request.user) # Pass user
            request_data_with_defaults = {
                'nodes': default_data['nodes_data'],
                'edges': default_data['edges_data']
            }
            serializer = self.get_serializer(instance, data=request_data_with_defaults, partial=False)
        else:
            serializer = self.get_serializer(instance, data=request.data, partial=not created)

        serializer.is_valid(raise_exception=True)
        serializer.save() 
        
        return Response(serializer.data, status=status.HTTP_200_OK if not created and (request.data.get('nodes') or request.data.get('edges')) else status.HTTP_201_CREATED)
    


from maintree.ai_model.ai_configuration import generate_family_tree_data, model
from .serializers import PromptSerializer

class GenerateFamilyTreeView(APIView):
    """
    API endpoint to generate family tree data from a natural language prompt.
    Requires JWT authentication.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        input_serializer = PromptSerializer(data=request.data)
        try:
            input_serializer.is_valid(raise_exception=True)
        except DRFValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        prompt_text = input_serializer.validated_data['prompt']

        if model is None:
             return Response(
                 {"error": "Family tree generation service is currently unavailable.",
                  "details": "AI model could not be configured."},
                 status=status.HTTP_503_SERVICE_UNAVAILABLE
             )


        try:
            family_tree_data_pydantic = generate_family_tree_data(prompt_text)
            response_data = family_tree_data_pydantic.model_dump(mode='json', by_alias=True)
            return Response(response_data, status=status.HTTP_200_OK)

        except PydanticValidationError as e:
            return Response(
                {"error": "Failed to validate AI response against schema.",
                 "details": json.loads(e.json())
                },
                status=status.HTTP_400_BAD_REQUEST 
            )
        except json.JSONDecodeError as e:
             return Response(
                {"error": "AI returned invalid JSON.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
             )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error processing family tree prompt: {e}", exc_info=True)

            return Response(
                {"error": "An internal error occurred while processing the request.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )