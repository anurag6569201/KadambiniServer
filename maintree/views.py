# familytree/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import UserFamilyTree
from .serializers import UserFamilyTreeSerializer
from .utils import get_default_family_tree_data

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