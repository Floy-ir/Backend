from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('', views.AccountViewSet, basename='accounts')

urlpatterns = [
    path('', include(router.urls)),
    path('send-otp/', views.AccountViewSet.as_view({'post': 'send_otp'}), name='send-otp'),
    path('verify-otp/', views.AccountViewSet.as_view({'post': 'verify_otp'}), name='verify-otp'),
    path('signup/', views.AccountViewSet.as_view({'post': 'signup'}), name='signup'),
    path('login/', views.AccountViewSet.as_view({'post': 'login'}), name='login'),
    path('forgot-password/', views.AccountViewSet.as_view({'post': 'forgot_password'}), name='forgot-password'),
    path('reset-password/', views.AccountViewSet.as_view({'post': 'reset_password'}), name='reset-password'),
]
