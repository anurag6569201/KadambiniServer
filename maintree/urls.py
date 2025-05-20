from django.urls import path
from .views import UserFamilyTreeView
from maintree.views import GenerateFamilyTreeView,ModifyFamilyTreeView

app_name = 'maintree'

urlpatterns = [
    path('data/', UserFamilyTreeView.as_view(), name='user_family_tree'),
    path('generate/', GenerateFamilyTreeView.as_view(), name='generate_family_tree'),
    path('modify/', ModifyFamilyTreeView.as_view(), name='modify_family_tree'),
]