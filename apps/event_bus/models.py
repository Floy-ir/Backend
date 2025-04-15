from django.db import models


class EventOrCommand(models.Model):
    uid = models.CharField(max_length=128, unique=True)
    emitter_uid = models.CharField(max_length=128)
    event_type = models.CharField(max_length=128)
    payload_json = models.JSONField()
    #   TODO: if needs to deserialize, we need to capture at least the class path
    created_at = models.PositiveBigIntegerField()
