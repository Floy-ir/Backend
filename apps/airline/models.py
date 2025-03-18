from django.db import models


class Airline(models.Model):
    uid = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name