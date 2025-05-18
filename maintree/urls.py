from django.urls import path
from .views import UserFamilyTreeView
# from maintree.ai_model.llm_views import FamilyTreeChatCommandView

app_name = 'maintree'

urlpatterns = [
    path('data/', UserFamilyTreeView.as_view(), name='user_family_tree'),
    # path('chat/command/', FamilyTreeChatCommandView.as_view(), name='user_family_tree_chat_command'),
]