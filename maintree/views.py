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
    


from maintree.ai_model.ai_configuration import generate_family_tree_data, modify_family_tree_data, model as gemini_model
from .serializers import PromptSerializer,ModifyFamilyTreeSerializer

import logging
logger = logging.getLogger(__name__)

class GenerateFamilyTreeView(APIView):
    """
    API endpoint to generate a NEW family tree data from a natural language prompt.
    """
    permission_classes = [permissions.IsAuthenticated] # Or other appropriate permissions

    def post(self, request, *args, **kwargs):
        input_serializer = PromptSerializer(data=request.data)
        try:
            input_serializer.is_valid(raise_exception=True)
        except DRFValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        prompt_text = input_serializer.validated_data['prompt']

        if gemini_model is None:
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
            logger.error(f"Pydantic Validation Error during generation: {e.json()}", exc_info=True)
            return Response(
                {"error": "Failed to validate AI response against schema during generation.",
                 "details": json.loads(e.json()) # Pydantic's e.json() is already a JSON string
                },
                status=status.HTTP_400_BAD_REQUEST # Or HTTP_500_INTERNAL_SERVER_ERROR if it's an unexpected schema mismatch
            )
        except json.JSONDecodeError as e:
            logger.error(f"AI returned invalid JSON during generation: {e}", exc_info=True)
            return Response(
                {"error": "AI returned invalid JSON during generation.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
             )
        except ValueError as e: # Catch specific ValueErrors from our util, like model not configured
            logger.error(f"Value error during generation: {e}", exc_info=True)
            return Response(
                {"error": "Configuration or input error during generation.", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error processing family tree prompt (generation): {e}", exc_info=True)
            return Response(
                {"error": "An internal error occurred while processing the generation request.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ModifyFamilyTreeView(APIView):
    """
    API endpoint to modify an existing family tree data using a natural language prompt.
    """
    permission_classes = [permissions.IsAuthenticated] # Or other appropriate permissions

    def post(self, request, *args, **kwargs):
        input_serializer = ModifyFamilyTreeSerializer(data=request.data)
        try:
            input_serializer.is_valid(raise_exception=True)
        except DRFValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        modification_prompt = input_serializer.validated_data['modification_prompt']
        current_tree_data = input_serializer.validated_data['current_tree_data'] # This is already a Python dict

        if gemini_model is None:
             return Response(
                 {"error": "Family tree modification service is currently unavailable.",
                  "details": "AI model could not be configured."},
                 status=status.HTTP_503_SERVICE_UNAVAILABLE
             )

        try:
            # current_tree_data is already validated by the serializer if validation is thorough
            # and parsed from JSON string to Python dict.
            modified_tree_data_pydantic = modify_family_tree_data(current_tree_data, modification_prompt)
            response_data = modified_tree_data_pydantic.model_dump(mode='json', by_alias=True)
            
            # Optionally, save the modified_tree_data_pydantic to your UserFamilyTree model if you have one
            # user = request.user
            # UserFamilyTree.objects.update_or_create(
            #     user=user,
            #     defaults={'tree_data': response_data} # Ensure your model field can store this
            # )

            return Response(response_data, status=status.HTTP_200_OK)

        except PydanticValidationError as e:
            logger.error(f"Pydantic Validation Error during modification: {e.json()}", exc_info=True)
            return Response(
                {"error": "Failed to validate AI response against schema during modification.",
                 "details": json.loads(e.json())
                },
                status=status.HTTP_400_BAD_REQUEST # Or HTTP_500 if schema mismatch is unexpected
            )
        except json.JSONDecodeError as e:
            logger.error(f"AI returned invalid JSON during modification: {e}", exc_info=True)
            return Response(
                {"error": "AI returned invalid JSON during modification.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
             )
        except ValueError as e: # Catch specific ValueErrors from our util
            logger.error(f"Value error during modification: {e}", exc_info=True)
            return Response(
                {"error": "Configuration or input error during modification.", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error processing family tree modification: {e}", exc_info=True)
            return Response(
                {"error": "An internal error occurred while processing the modification request.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )