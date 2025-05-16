from django.db import models


class City(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100, unique=True)
    origin_cities = models.ManyToManyField(
        'self',
        blank=True,
        related_name='destinations',
        symmetrical=False
    )

    def __str__(self):
        return self.name
