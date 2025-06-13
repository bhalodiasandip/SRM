from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (    
    TokenRefreshView,
    TokenBlacklistView
)
from api import views

# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(r'requirements', views.RequirementViewSet, basename='requirement')
router.register(r'villages', views.VillageViewSet, basename='village')
router.register(r'areas', views.AreaViewSet, basename='area')
router.register(r'skills', views.SkillViewSet, basename='skill')
router.register(r'bids', views.BidViewSet, basename='bid')


# router.register(r'user-profile', views.UserProfileView, basename='user-profile')

# router.register(r'users', views.UserViewSet, basename='user')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
    path('my-requirements/', views.MyRequirementListView.as_view(), name='my-requirements'),
    path('user-profile/', views.UserProfileView.as_view(), name='user-profile'),
    path("register/", views.RegisterAPIView.as_view(), name="register"),
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
]
