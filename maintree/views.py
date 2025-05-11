from rest_framework import viewsets, status, generics, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import (
    FamilyTree, Person, Relationship, MedicalCondition,
    TimelineEvent, GeneticMarker, Document
)
from .serializers import (
    FamilyTreeSerializer, FamilyTreeDetailSerializer, FullTreeDataWriteSerializer,
    PersonSerializer, RelationshipSerializer, MedicalConditionSerializer,
    TimelineEventSerializer, GeneticMarkerSerializer, DocumentSerializer,
    CustomUserSimpleSerializer 
)
import requests 

User = settings.AUTH_USER_MODEL

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSimpleSerializer 
    permission_classes = [AllowAny]


class FamilyTreeViewSet(viewsets.ModelViewSet):
    serializer_class = FamilyTreeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FamilyTree.objects.filter(owner=self.request.user).prefetch_related('persons', 'relationships')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'get_tree_data':
            return FamilyTreeDetailSerializer
        return FamilyTreeSerializer

    @action(detail=True, methods=['get'], url_path='data', serializer_class=FamilyTreeDetailSerializer)
    def get_tree_data(self, request, pk=None):
        """
        Retrieves all persons (nodes) and relationships (edges) for a specific family tree.
        """
        tree = self.get_object()
        serializer = self.get_serializer(tree)

        # The FamilyTreeDetailSerializer now has 'persons' and 'relationships' directly
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='data', serializer_class=FullTreeDataWriteSerializer)
    def save_tree_data(self, request, pk=None):
        """
        Saves the entire tree structure (nodes and edges).
        This will replace the existing nodes and edges for the tree.
        """
        tree = self.get_object()
        serializer = FullTreeDataWriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(tree_instance=tree) 
            updated_tree_serializer = FamilyTreeDetailSerializer(tree)
            return Response(updated_tree_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseTreeResourceViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet for resources that belong to a FamilyTree and a User.
    Ensures that users can only interact with resources in their own trees.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset_for_tree(self, tree_pk):
        # Example: return Person.objects.filter(tree_id=tree_pk, tree__owner=self.request.user)
        raise NotImplementedError("Subclasses must implement get_queryset_for_tree.")

    def get_queryset(self):
        # Allow listing all if no tree_pk in URL, but filtered by owner
        # Or, enforce tree_pk for all list actions if preferred
        tree_pk = self.kwargs.get('tree_pk')
        if tree_pk:
            return self.get_queryset_for_tree(tree_pk)
        return self.serializer_class.Meta.model.objects.none() 

    def perform_create(self, serializer):
        tree_pk = self.kwargs.get('tree_pk')
        tree = get_object_or_404(FamilyTree, pk=tree_pk, owner=self.request.user)
        serializer.save(tree=tree) 

class PersonViewSet(BaseTreeResourceViewSet):
    serializer_class = PersonSerializer
    def get_queryset_for_tree(self, tree_pk):
        return Person.objects.filter(tree_id=tree_pk, tree__owner=self.request.user).prefetch_related(
            'medical_conditions', 'timeline_events'
        )
    def perform_create(self, serializer):
        tree_pk = self.request.data.get('tree_id')
        if not tree_pk and 'tree_pk' in self.kwargs:
            tree_pk = self.kwargs['tree_pk']

        if not tree_pk:
            raise serializers.ValidationError("Tree ID is required to create a person.")
        tree = get_object_or_404(FamilyTree, pk=tree_pk, owner=self.request.user)
        serializer.save(tree=tree)


class RelationshipViewSet(BaseTreeResourceViewSet):
    serializer_class = RelationshipSerializer
    def get_queryset_for_tree(self, tree_pk):
        return Relationship.objects.filter(tree_id=tree_pk, tree__owner=self.request.user)

# For nested resources like MedicalCondition under a Person
class NestedPersonResourceViewSet(mixins.CreateModelMixin,
                                  mixins.UpdateModelMixin,
                                  mixins.DestroyModelMixin,
                                  mixins.ListModelMixin, 
                                  mixins.RetrieveModelMixin, 
                                  viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_person_object(self):
        person_rf_node_id = self.kwargs.get('person_rf_node_id')
        tree_pk = self.kwargs.get('tree_pk') 
        person = get_object_or_404(
            Person,
            react_flow_node_id=person_rf_node_id,
            tree_id=tree_pk,
            tree__owner=self.request.user
        )
        return person

    def get_queryset(self):
        person = self.get_person_object()
        return getattr(person, self.queryset_related_name).all()


    def perform_create(self, serializer):
        person = self.get_person_object()
        serializer.save(person=person)

class MedicalConditionViewSet(NestedPersonResourceViewSet):
    serializer_class = MedicalConditionSerializer
    queryset_related_name = 'medical_conditions' 

class TimelineEventViewSet(NestedPersonResourceViewSet):
    serializer_class = TimelineEventSerializer
    queryset_related_name = 'timeline_events'

class GeneticMarkerViewSet(NestedPersonResourceViewSet):
    serializer_class = GeneticMarkerSerializer
    queryset_related_name = 'genetic_markers'

class DocumentViewSet(NestedPersonResourceViewSet):
    serializer_class = DocumentSerializer
    queryset_related_name = 'documents'


# --- MedlinePlus Proxy View (Example as discussed previously) ---
def medlineplus_proxy_view(request):
    search_term = request.GET.get('term', '')
    if not search_term:
        return Response({'error': 'No search term provided'}, status=status.HTTP_400_BAD_REQUEST)

    api_url = "https://wsearch.nlm.nih.gov/ws/query"
    params = {'db': 'healthTopics', 'term': search_term, 'retmax': 10, 'rettype': 'brief'}
    headers = {'Accept': 'application/json'} 

    try:
        api_response = requests.get(api_url, params=params, headers=headers, timeout=10)
        api_response.raise_for_status()
        
        # NLM Health Topics search API returns JSON directly if 'Accept: application/json' is sent.
        # The JSON structure is:
        # { "nlmSearchResult": { "list": [ { "title": "...", "snippet": "...", "url": "..." } ] } }
        data = api_response.json()
        
        results = []
        if data.get("nlmSearchResult") and data["nlmSearchResult"].get("list"):
            for item_list in data["nlmSearchResult"]["list"]:
                 for item in item_list.get("document", []):
                    title_content = ""
                    # Title can be complex, extract string
                    if isinstance(item.get("title"), list): 
                        for t_part in item["title"]:
                            if t_part.get("@name") == "title" and t_part.get("content"):
                                title_content = t_part["content"]
                                break
                    elif isinstance(item.get("title"), dict): 
                         title_content = item["title"].get("content", "")

                    snippet_content = ""
                    if isinstance(item.get("snippet"), list):
                         for s_part in item["snippet"]:
                            if s_part.get("@name") == "snippet" and s_part.get("content"):
                                snippet_content = s_part["content"]
                                break
                    elif isinstance(item.get("snippet"), dict):
                         snippet_content = item["snippet"].get("content", "")
                    
                    results.append({
                        "name": title_content,
                        "description": snippet_content,
                        "url": item.get("url"),
                        # "code": item.get("some_code_field") # If available
                    })

        return Response({"results": results})

    except requests.exceptions.Timeout:
        return Response({'error': 'Request to MedlinePlus API timed out'}, status=status.HTTP_504_GATEWAY_TIMEOUT)
    except requests.exceptions.RequestException as e:
        return Response({'error': f'MedlinePlus API request failed: {str(e)}'}, status=status.HTTP_502_BAD_GATEWAY)
    except ValueError as e:
        return Response({'error': f'Failed to parse MedlinePlus API response: {str(e)}', 'raw_response': api_response.text if 'api_response' in locals() else 'N/A'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)