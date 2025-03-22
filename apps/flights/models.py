from django.db import models


class Flight(models.Model):
    FIRST_CLASS = 'First Class'
    BUSINESS_CLASS = 'Business Class'
    PREMIUM_ECONOMY = 'Premium Economy'
    ECONOMY_CLASS = 'Economy Class'
    BASIC_ECONOMY = 'Basic Economy'

    SEAT_CLASSES = [
        (FIRST_CLASS, 'First Class'),
        (BUSINESS_CLASS, 'Business Class'),
        (PREMIUM_ECONOMY, 'Premium Economy'),
        (ECONOMY_CLASS, 'Economy Class'),
        (BASIC_ECONOMY, 'Basic Economy'),
    ]

    uid = models.CharField(max_length=128, unique=True)
    airline = models.CharField(max_length=128)
    origin = models.CharField(max_length=64)
    destination = models.CharField(max_length=64)
    departure_timestamp = models.BigIntegerField()
    arrival_timestamp = models.BigIntegerField()
    allowed_weight = models.IntegerField()
    seat_class = models.CharField(
        max_length=20,
        choices=SEAT_CLASSES,
        default=ECONOMY_CLASS,
    )

    def __str__(self):
        return f"{self.airline} {self.origin} -> {self.destination} ({self.seat_class})"


class Website(models.Model):
    uid = models.CharField(max_length=128, unique=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=15, decimal_places=3)
    redirect_url = models.CharField(max_length=128)
    remaining_seat = models.IntegerField()
    is_valid = models.BooleanField(default=True)
    last_modified_at = models.BigIntegerField()

    def __str__(self):
        return f"Website {self.uid} for Flight {self.flight.uid}"

