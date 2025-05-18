# familytree/models.py
from django.db import models
from django.conf import settings # To get the AUTH_USER_MODEL

class UserFamilyTree(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='family_tree_data' # Changed related_name to avoid conflict if 'family_tree' is used elsewhere
    )
    nodes_data = models.JSONField(default=list) # Stores the array of nodes
    edges_data = models.JSONField(default=list) # Stores the array of edges
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Family Tree for {self.user.username}"