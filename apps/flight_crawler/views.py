from rest_framework import viewsets, response
from runner.bootstrap import get_bootstrapper
from . import interfaces


class WebsiteViewSet(viewsets.GenericViewSet):
    def create(self, request):
        service = get_bootstrapper().get_flight_crawler_service()
        files = request.FILES.getlist('logo') 

        file_objects = []
        for file in files:
            file_objects.append({
                'name': file.name,
                'buffer': file.read()
            })

        upload_request_data = {
            'uid': request.data['uid'],  # Ensure 'uid' is in the form data
            'logo': file_objects[0]
        }

        upload_request = interfaces.UploadImageRequest(**upload_request_data)

        results = service.upload_image(request=upload_request)
        return response.Response(results.model_dump())
