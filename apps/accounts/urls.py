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
    path('eitaa/', views.AccountViewSet.as_view({'post': 'eita_login'}), name='eita-login'),
    path('send-eita-message/', views.AccountViewSet.as_view({'post': 'send_eita_message'}), name='send-eita-message'),
    path('bale/', views.AccountViewSet.as_view({'post': 'bale_login'}), name='bale-login'),
    path('send-bale-message/', views.AccountViewSet.as_view({'post': 'send_bale_message'}), name='send-bale-message'),
    path('telegram/', views.AccountViewSet.as_view({'post': 'telegram_login'}), name='telegram-login'),
    path('send-telegram-message/', views.AccountViewSet.as_view({'post': 'send_telegram_message'}), name='send-telegram-message'),
]
