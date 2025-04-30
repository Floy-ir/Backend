from django.contrib import admin
from .models import Flight, Website

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('uid', 'airline', 'origin', 'destination', 'departure_timestamp', 'arrival_timestamp', 
                   'seat_class', 'cheapest_price', 'cheapest_website_uid')
    list_filter = ('seat_class', 'airline')
    search_fields = ('uid', 'airline', 'origin', 'destination')
    readonly_fields = ('uid',)
    ordering = ('-departure_timestamp',)

@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ('uid', 'flight', 'adult_price', 'child_price', 'infant_price', 'remaining_seat', 'is_valid')
    list_filter = ('is_valid',)
    search_fields = ('uid', 'flight__uid', 'flight__airline')
    raw_id_fields = ('flight',)
    readonly_fields = ('uid', 'last_crawled_uid') 