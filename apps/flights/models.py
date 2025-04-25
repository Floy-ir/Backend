from django.db import models
from django.db.models import Count, Q


class FlightManager(models.Manager):
    def filter_flights_by_sites(self, website_uids, website_filters, flight_filters, prefetch_websites=True):
        queryset = self.get_queryset()

        if flight_filters:
            queryset = queryset.filter(**flight_filters)

        if website_filters:
            website_q = Q(**website_filters)
            queryset = queryset.filter(website_q)

        if website_uids:
            queryset = queryset.filter(websites__uid__in=website_uids)

        if prefetch_websites:
            queryset = queryset.prefetch_related('websites')

        return queryset.distinct()

# TODO: add crcn policy for every website

class Flight(models.Model):
    FIRST_CLASS = 'First Class'
    BUSINESS_CLASS = 'Business Class'
    PREMIUM_ECONOMY = 'Premium Economy'
    ECONOMY_CLASS = 'Economy Class'
    BASIC_ECONOMY = 'Basic Economy'

    SEAT_CLASSES = [
        (FIRST_CLASS, 'First'),
        (BUSINESS_CLASS, 'Business'),
        (PREMIUM_ECONOMY, 'Premium Economy'),
        (ECONOMY_CLASS, 'Economy'),
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
    cheapest_price = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=True)
    cheapest_base_redirect_url = models.CharField(max_length=256, null=True, blank=True)
    cheapest_one_adult_redirect_url = models.CharField(max_length=256, null=True, blank=True)
    cheapest_two_adult_redirect_url = models.CharField(max_length=256, null=True, blank=True)
    cheapest_website_uid = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.airline} {self.origin} -> {self.destination} ({self.seat_class})"

    def update_cheapest_info(self):
        """
        Updates the cheapest price, redirect URL, and website UID based on valid websites.
        """
        valid_websites = self.websites.filter(is_valid=True)
        if not valid_websites.exists():
            self.cheapest_price = None
            self.cheapest_base_redirect_url = None
            self.cheapest_one_adult_redirect_url = None
            self.cheapest_two_adult_redirect_url = None
            self.cheapest_website_uid = None
            self.save()
            return
            
        cheapest_website = min(valid_websites, key=lambda w: w.adult_price)
        self.cheapest_price = cheapest_website.adult_price
        self.cheapest_base_redirect_url = cheapest_website.base_redirect_url
        self.cheapest_one_adult_redirect_url = cheapest_website.one_adult_redirect_url
        self.cheapest_two_adult_redirect_url = cheapest_website.two_adult_redirect_url
        self.cheapest_website_uid = cheapest_website.uid
        self.save()

    objects = FlightManager()


class Website(models.Model):
    uid = models.CharField(max_length=128)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='websites')
    adult_price = models.FloatField(null=True, blank=True)
    child_price = models.FloatField(null=True, blank=True)
    infant_price = models.FloatField(null=True, blank=True)
    base_redirect_url = models.CharField(max_length=128)
    one_adult_redirect_url = models.CharField(max_length=128, null=True, blank=True)
    two_adult_redirect_url = models.CharField(max_length=128, null=True, blank=True)
    remaining_seat = models.IntegerField()
    is_valid = models.BooleanField(default=True)
    last_crawled_uid = models.CharField(max_length=128)

    def __str__(self):
        return f"Website {self.uid} for Flight {self.flight.uid}"
