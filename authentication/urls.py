from django.urls import path
from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    UserInfoView,
    LogoutView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/', UserInfoView.as_view(), name='user_info'),
]