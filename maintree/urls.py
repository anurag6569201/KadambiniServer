from django.urls import path
from .views import UserFamilyTreeView

app_name = 'maintree'

urlpatterns = [
    path('data/', UserFamilyTreeView.as_view(), name='user_family_tree'),
]