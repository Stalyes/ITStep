from django.contrib import admin
from .models import Station, Train, Wagon, Seat, Passenger, Booking, Ticket, Payment

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = ('id', 'train_number', 'train_name', 'departure_city', 'arrival_city', 'weekday', 'departure_time')
    list_filter = ('weekday', 'departure_city', 'arrival_city')

@admin.register(Wagon)
class WagonAdmin(admin.ModelAdmin):
    list_display = ('id', 'train', 'wagon_number', 'wagon_class')

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('id', 'wagon', 'seat_label', 'price')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('ticket_code', 'train', 'departure_city', 'arrival_city', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'departure_date')

admin.site.register(Passenger)
admin.site.register(Ticket)
admin.site.register(Payment)