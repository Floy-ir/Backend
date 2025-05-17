from django.db import models


class Airline(models.Model):
    uid = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=64, unique=True)
    image = models.CharField(max_length=1024, blank=True, null=True)

    def __str__(self):
        return self.name