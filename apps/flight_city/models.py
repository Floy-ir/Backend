from django.db import models


class City(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    origin_city = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='destinations'
    )

    def __str__(self):
        return self.name
