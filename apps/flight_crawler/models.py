from django.db import models

class Website(models.Model):
    uid = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255, unique=True)
    name_fa = models.CharField(max_length=255, unique=True)
    logo = models.CharField(max_length=255)
    base_url = models.URLField()
    request_method = models.CharField(max_length=10, choices=[("GET", "GET"), ("POST", "POST")])
    request_headers = models.JSONField(default=dict, blank=True)
    request_payload_structure = models.JSONField(default=dict, blank=True)
    response_parsing_rules = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class WebsiteRoute(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name="routes")
    origin = models.CharField(max_length=5)
    destination = models.CharField(max_length=5)
    is_supported = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ("website", "origin", "destination")

    def __str__(self):
        return f"{self.website.name}: {self.origin} → {self.destination}"

