from django.http import JsonResponse
from rest_framework import viewsets, permissions, response
from rest_framework.decorators import action
from runner.bootstrap import get_bootstrapper
from . import interfaces as interfaces

class StatisticsViewSet(viewsets.GenericViewSet):
    # permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        service = get_bootstrapper().get_statistic_service()
        request = interfaces.IncreaseRedirectNumberRequest(**request.data)
        service.increase_redirect(request=request)
        return JsonResponse({"success": True}, status=200)
    
    def list(self, request):
        service = get_bootstrapper().get_statistic_service()
        result = service.get_providers()
        return response.Response(result.model_dump())
