from django.db import models
from django.conf import settings
import uuid

# Using settings.AUTH_USER_MODEL to refer to your CustomUser
User = settings.AUTH_USER_MODEL

class FamilyTree(models.Model):
    owner = models.ForeignKey(User, related_name='family_trees', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default='My Family Tree')
    visibility = models.CharField(max_length=50, default='private', choices=[('private', 'Private'), ('shared', 'Shared'), ('public', 'Public')])
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('owner', 'name')

    def __str__(self):
        return f"{self.name} (Owner: {self.owner.username})"

class Person(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'), ('female', 'Female'), ('other', 'Other'), ('unknown', 'Unknown')
    ]
    LIFESTYLE_SMOKER_CHOICES = [
        ('unknown', 'Unknown'), ('yes', 'Yes'), ('no', 'No'), ('former', 'Former')
    ]
    LIFESTYLE_DRINKER_CHOICES = [
        ('unknown', 'Unknown'), ('yes', 'Regularly'), ('socially', 'Socially'), ('no', 'No'), ('former', 'Former')
    ]

    tree = models.ForeignKey(FamilyTree, related_name='persons', on_delete=models.CASCADE)
    react_flow_node_id = models.CharField(max_length=255, db_index=True)

    # React Flow specific data
    position_x = models.FloatField(null=True, blank=True)
    position_y = models.FloatField(null=True, blank=True)

    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='unknown')
    dob = models.DateField(null=True, blank=True, verbose_name="Date of Birth")
    dod = models.DateField(null=True, blank=True, verbose_name="Date of Death")
    photo_url = models.URLField(max_length=1024, null=True, blank=True) # Increased length for potential base64

    # Lifestyle
    occupation = models.CharField(max_length=255, blank=True, null=True)
    smoker_status = models.CharField(max_length=10, choices=LIFESTYLE_SMOKER_CHOICES, default='unknown')
    drinker_status = models.CharField(max_length=10, choices=LIFESTYLE_DRINKER_CHOICES, default='unknown')
    diet = models.CharField(max_length=100, blank=True, null=True)
    activity_level = models.CharField(max_length=100, blank=True, null=True)

    notes = models.TextField(blank=True, null=True)

    # Smart Health Mock Properties
    hereditary_risk_score = models.IntegerField(default=0, null=True, blank=True)
    is_hereditary_risk_calculated = models.BooleanField(default=False)

    # Contact Info (can be a JSONField if your DB supports it, or individual fields)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=30, blank=True, null=True)
    contact_address = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # A person's react_flow_node_id must be unique within its FamilyTree
        unique_together = ('tree', 'react_flow_node_id')
        ordering = ['full_name']

    def __str__(self):
        return f"{self.full_name} (Tree: {self.tree.name}, RF_ID: {self.react_flow_node_id})"

class Relationship(models.Model):
    tree = models.ForeignKey(FamilyTree, related_name='relationships', on_delete=models.CASCADE)

    # This ID comes from React Flow and must be unique *within this tree*
    react_flow_edge_id = models.CharField(max_length=255, db_index=True)

    # Storing React Flow node IDs for source and target directly
    source_person_rf_node_id = models.CharField(max_length=255)
    target_person_rf_node_id = models.CharField(max_length=255)

    # Optional: If you want to enforce ForeignKey constraints to actual Person objects
    # after they are created. This makes direct creation harder if persons don't exist yet.
    # source_person_obj = models.ForeignKey(Person, related_name='source_for_edges', on_delete=models.CASCADE, null=True, blank=True)
    # target_person_obj = models.ForeignKey(Person, related_name='target_for_edges', on_delete=models.CASCADE, null=True, blank=True)

    label = models.CharField(max_length=100) # e.g., Spouse, Parent-Child
    relationship_type = models.CharField(max_length=50, blank=True, null=True) # More specific, e.g., from RELATIONSHIP_TYPES
    relationship_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    # React Flow specific edge data (can be stored as JSON or individual fields)
    edge_animated = models.BooleanField(default=False)
    edge_type_rf = models.CharField(max_length=50, default='smoothstep') # e.g., 'smoothstep', 'default'
    
    # For style, it's often better to let frontend handle it or store as JSON if complex
    # edge_style_stroke = models.CharField(max_length=50, blank=True, null=True)
    # edge_style_stroke_width = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # An edge's react_flow_edge_id must be unique within its FamilyTree
        unique_together = ('tree', 'react_flow_edge_id')

    def __str__(self):
        return f"Edge: {self.source_person_rf_node_id} -({self.label})-> {self.target_person_rf_node_id} (Tree: {self.tree.name})"

class MedicalCondition(models.Model):
    person = models.ForeignKey(Person, related_name='medical_conditions', on_delete=models.CASCADE)
    condition_name = models.CharField(max_length=255)
    condition_code = models.CharField(max_length=50, blank=True, null=True) # e.g., ICD-10, SNOMED
    category = models.CharField(max_length=100, blank=True, null=True)
    onset_age = models.PositiveIntegerField(null=True, blank=True)
    is_hereditary = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    custom_flag = models.BooleanField(default=True)

    class Meta:
        ordering = ['condition_name']

    def __str__(self):
        return f"{self.condition_name} ({self.person.full_name})"

class TimelineEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ('Birth', 'Birth'), ('Death', 'Death'), ('Marriage', 'Marriage'),
        ('Diagnosis', 'Diagnosis'), ('Procedure', 'Procedure'), ('Custom', 'Custom')
    ]
    person = models.ForeignKey(Person, related_name='timeline_events', on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    date = models.DateField()
    description = models.TextField()

    class Meta:
        ordering = ['date', 'event_type']

    def __str__(self):
        return f"{self.event_type} on {self.date} for {self.person.full_name}"

# --- Placeholder Models for future expansion ---
class GeneticMarker(models.Model):
    person = models.ForeignKey(Person, related_name='genetic_markers', on_delete=models.CASCADE)
    marker_id = models.CharField(max_length=100, blank=True, null=True) # e.g., rsID
    gene_name = models.CharField(max_length=100, blank=True, null=True)
    variant_info = models.CharField(max_length=255, blank=True, null=True) # e.g., C/T
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Marker {self.marker_id or self.gene_name} for {self.person.full_name}"

class Document(models.Model):
    person = models.ForeignKey(Person, related_name='documents', on_delete=models.CASCADE)
    document_name = models.CharField(max_length=255)
    document_type = models.CharField(max_length=100, blank=True, null=True) # e.g., Medical Report, Genetic Test
    upload_date = models.DateField(auto_now_add=True)

    # For actual file uploads, use FileField. For links, URLField.
    # file = models.FileField(upload_to=f'documents/{person.id}/', blank=True, null=True) # Needs dynamic path
    
    file_url = models.URLField(max_length=1024, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Document '{self.document_name}' for {self.person.full_name}"