from django.db import models

class Statistic(models.Model):
    uid = models.CharField(max_length=128, unique=True)
    provider = models.CharField(max_length=256, unique=True)
    redirect_number = models.IntegerField()

    def __str__(self):
        return self.provider