# familytree/serializers.py
from rest_framework import serializers
from .models import UserFamilyTree
from datetime import datetime # Import datetime
from .ai_model.ai_pydentic_model import FamilyTreeData

class UserFamilyTreeSerializer(serializers.ModelSerializer):
    nodes = serializers.ListField(child=serializers.DictField(), source='nodes_data', required=True)
    edges = serializers.ListField(child=serializers.DictField(), source='edges_data', required=True)

    class Meta:
        model = UserFamilyTree
        fields = ['nodes', 'edges', 'last_modified']
        read_only_fields = ['last_modified']

    def create(self, validated_data):
        user = self.context['request'].user
        tree, created = UserFamilyTree.objects.update_or_create(
            user=user,
            defaults=validated_data
        )
        return tree

    def update(self, instance, validated_data):
        instance.nodes_data = validated_data.get('nodes_data', instance.nodes_data)
        instance.edges_data = validated_data.get('edges_data', instance.edges_data)
        instance.save()
        return instance

    def to_representation(self, instance):
        # Handle case where last_modified might be None for unsaved instances
        last_modified_iso = None
        if instance.last_modified:
            last_modified_iso = instance.last_modified.isoformat()
        elif instance.pk: # If it has a PK, it should have a last_modified, but as a fallback
            last_modified_iso = datetime.now().isoformat() # Fallback for saved instance missing it
        # For a completely new, unsaved instance being represented (e.g. default data for GET),
        # last_modified_iso will remain None, which is acceptable for the client.

        return {
            "nodes": instance.nodes_data,
            "edges": instance.edges_data,
            "last_modified": last_modified_iso 
        }
    

class PromptSerializer(serializers.Serializer):
    prompt = serializers.CharField()

class ModifyFamilyTreeSerializer(serializers.Serializer):
    modification_prompt = serializers.CharField(help_text="Natural language instructions for modifying the tree.")
    current_tree_data = serializers.JSONField(help_text="The current FamilyTreeData JSON object.")

    def validate_current_tree_data(self, value):
        try:
            # Validate the incoming JSON against the Pydantic model
            FamilyTreeData.model_validate(value)
            return value # Return the parsed and validated Python dict
        except Exception as e: # Catches Pydantic's ValidationError and others
            raise serializers.ValidationError(f"Invalid current_tree_data: {e}")