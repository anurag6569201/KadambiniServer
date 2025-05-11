from rest_framework import serializers
from django.conf import settings
from .models import (
    FamilyTree, Person, Relationship, MedicalCondition,
    TimelineEvent, GeneticMarker, Document
)

User = settings.AUTH_USER_MODEL

class CustomUserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

# --- Nested Serializers for Person details ---
class MedicalConditionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False) 
    class Meta:
        model = MedicalCondition
        exclude = ['person'] 

class TimelineEventSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = TimelineEvent
        exclude = ['person']

class GeneticMarkerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = GeneticMarker
        exclude = ['person']

class DocumentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = Document
        exclude = ['person']

class PersonSerializer(serializers.ModelSerializer):
    medical_conditions = MedicalConditionSerializer(many=True, required=False)
    timeline_events = TimelineEventSerializer(many=True, required=False)
    genetic_markers = GeneticMarkerSerializer(many=True, required=False, read_only=True) # Read-only for now
    documents = DocumentSerializer(many=True, required=False, read_only=True) # Read-only for now

    class Meta:
        model = Person
        fields = [
            # 'id', # Django's auto ID, not react_flow_node_id for this field context
            'react_flow_node_id', 'position_x', 'position_y', 'full_name', 'gender',
            'dob', 'dod', 'photo_url', 'occupation', 'smoker_status', 'drinker_status',
            'diet', 'activity_level', 'notes', 'hereditary_risk_score', 'is_hereditary_risk_calculated',
            'contact_email', 'contact_phone', 'contact_address',
            'medical_conditions', 'timeline_events', 'genetic_markers', 'documents'
        ]

    def _handle_nested_items(self, instance, items_data, item_model, item_serializer_class, related_manager_name):
        # items_data is a list of dicts from validated_data
        item_ids_to_keep = []

        if items_data is not None:
            for item_data in items_data:
                item_id = item_data.get('id', None)
                if item_id: 
                    try:
                        item_instance = item_model.objects.get(id=item_id, person=instance)
                        # item_serializer = item_serializer_class(item_instance, data=item_data) 
                        for attr, value in item_data.items():
                            setattr(item_instance, attr, value)
                        item_instance.save()
                        item_ids_to_keep.append(item_instance.id)
                    except item_model.DoesNotExist:
                        # Item with this ID doesn't exist or doesn't belong to this person
                        pass 
                else: # New item, create it
                    new_item = item_model.objects.create(person=instance, **item_data)
                    item_ids_to_keep.append(new_item.id)

        # Delete items not in the payload (if items_data was provided)
        if items_data is not None:
            related_manager = getattr(instance, related_manager_name)
            related_manager.exclude(id__in=item_ids_to_keep).delete()


    def create(self, validated_data):
        medical_conditions_data = validated_data.pop('medical_conditions', [])
        timeline_events_data = validated_data.pop('timeline_events', [])

        # genetic_markers_data = validated_data.pop('genetic_markers', []) # if writable
        # documents_data = validated_data.pop('documents', []) # if writable

        # `tree` needs to be passed from the view, e.g. via serializer context
        # person = Person.objects.create(tree=self.context['tree'], **validated_data)
        # For the FullTreeDataWriteSerializer, tree is already associated.

        person = Person.objects.create(**validated_data)


        self._handle_nested_items(person, medical_conditions_data, MedicalCondition, MedicalConditionSerializer, 'medical_conditions')
        self._handle_nested_items(person, timeline_events_data, TimelineEvent, TimelineEventSerializer, 'timeline_events')
        # self._handle_nested_items(person, genetic_markers_data, ...)
        # self._handle_nested_items(person, documents_data, ...)
        return person

    def update(self, instance, validated_data):
        medical_conditions_data = validated_data.pop('medical_conditions', None)
        timeline_events_data = validated_data.pop('timeline_events', None)
        # genetic_markers_data = validated_data.pop('genetic_markers', None)
        # documents_data = validated_data.pop('documents', None)

        # Update Person instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle nested updates/creations/deletions
        self._handle_nested_items(instance, medical_conditions_data, MedicalCondition, MedicalConditionSerializer, 'medical_conditions')
        self._handle_nested_items(instance, timeline_events_data, TimelineEvent, TimelineEventSerializer, 'timeline_events')
        # self._handle_nested_items(instance, genetic_markers_data, ...)
        # self._handle_nested_items(instance, documents_data, ...)
        return instance

class RelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relationship
        fields = [
            # 'id',
            'react_flow_edge_id', 'source_person_rf_node_id', 'target_person_rf_node_id',
            'label', 'relationship_type', 'relationship_date', 'notes',
            'edge_animated', 'edge_type_rf'
        ]
        # `tree` field will be handled by the view context

class FamilyTreeSerializer(serializers.ModelSerializer):
    owner = CustomUserSimpleSerializer(read_only=True)
    persons_count = serializers.SerializerMethodField()
    relationships_count = serializers.SerializerMethodField()

    class Meta:
        model = FamilyTree
        fields = ['id', 'owner', 'name', 'visibility', 'description', 'created_at', 'updated_at', 'persons_count', 'relationships_count']

    def get_persons_count(self, obj):
        return obj.persons.count()

    def get_relationships_count(self, obj):
        return obj.relationships.count()

# Serializer for GETting a tree with all its nodes and edges
class FamilyTreeDetailSerializer(serializers.ModelSerializer):
    owner = CustomUserSimpleSerializer(read_only=True)
    persons = PersonSerializer(many=True, read_only=True) # nodes
    relationships = RelationshipSerializer(many=True, read_only=True) # edges

    class Meta:
        model = FamilyTree
        fields = ['id', 'owner', 'name', 'visibility', 'description', 'persons', 'relationships', 'created_at', 'updated_at']

# Serializer for POSTing the entire tree structure (nodes and edges)
class FullTreeDataWriteSerializer(serializers.Serializer):
    # `treeName` can update the FamilyTree.name if needed, or just be for reference
    # treeName = serializers.CharField(max_length=255, required=False)
    nodes = PersonSerializer(many=True) 
    edges = RelationshipSerializer(many=True)

    def save(self, tree_instance):
        nodes_data = self.validated_data.get('nodes', [])
        edges_data = self.validated_data.get('edges', [])

        # Strategy: Delete existing and recreate. Simpler than diffing.
        tree_instance.persons.all().delete() 
        tree_instance.relationships.all().delete()

        # Create Persons
        for node_payload in nodes_data:
            Person.objects.create(tree=tree_instance, **node_payload)

        # Create Relationships
        for edge_payload in edges_data:
            Relationship.objects.create(tree=tree_instance, **edge_payload)

        # Optionally update tree name
        # tree_name = self.validated_data.get('treeName')
        # if tree_name:
        #     tree_instance.name = tree_name
        #     tree_instance.save()
        return tree_instance