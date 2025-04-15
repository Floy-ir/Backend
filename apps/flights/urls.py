from django.urls import path, include
from rest_framework import routers
from . import views


router = routers.DefaultRouter()

router.register('', views.FlightsViewSet, basename='flights')

urlpatterns = [
    path('', include(router.urls)),
    path('cheapest/', views.FlightsViewSet.as_view({'get': 'get_cheapest_ticket'}), name='cheapest-tickets'),
]
