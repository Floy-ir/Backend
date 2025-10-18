from django.urls import path, include
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register('', views.AIAgentViewSet, basename='ai_agent')

urlpatterns = [
    path('', include(router.urls)),
    path('chat/', views.AIAgentViewSet.as_view({'post': 'chat'}), name='ai-agent-chat'),
    path('conversation/', views.AIAgentViewSet.as_view({'post': 'conversation'}), name='ai-agent-conversation'),
    path('search-flights/', views.AIAgentViewSet.as_view({'post': 'search_flights'}), name='ai-agent-search-flights'),
    path('cheapest-flights/', views.AIAgentViewSet.as_view({'post': 'get_cheapest_flights'}), name='ai-agent-cheapest-flights'),
    path('search-cities/', views.AIAgentViewSet.as_view({'get': 'search_cities'}), name='ai-agent-search-cities'),
    path('search-airlines/', views.AIAgentViewSet.as_view({'get': 'search_airlines'}), name='ai-agent-search-airlines'),
    path('function-schema/', views.AIAgentViewSet.as_view({'get': 'get_function_schema'}), name='ai-agent-function-schema'),
]
