from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

DAYS_KA = [
    ("ორშაბათი", "ორშაბათი"),
    ("სამშაბათი", "სამშაბათი"),
    ("ოთხშაბათი", "ოთხშაბათი"),
    ("ხუთშაბათი", "ხუთშაბათი"),
    ("პარასკევი", "პარასკევი"),
    ("შაბათი", "შაბათი"),
    ("კვირა", "კვირა"),
]

class Station(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'stations'

    def __str__(self):
        return self.name

class Train(models.Model):
    train_number = models.IntegerField()
    train_name = models.CharField(max_length=150)
    departure_city = models.CharField(max_length=100)
    arrival_city = models.CharField(max_length=100)
    weekday = models.CharField(max_length=50, choices=DAYS_KA)
    departure_time = models.CharField(max_length=10)
    arrival_time = models.CharField(max_length=10)

    class Meta:
        db_table = 'trains'

    def __str__(self):
        return f"#{self.train_number} {self.train_name} ({self.weekday})"

class Wagon(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='wagons')
    wagon_number = models.IntegerField()
    wagon_class = models.CharField(max_length=50, default="II კლასი")

    class Meta:
        db_table = 'wagons'

    def __str__(self):
        return f"Wagon #{self.wagon_number} ({self.wagon_class}) - Train #{self.train.train_number}"

class Seat(models.Model):
    wagon = models.ForeignKey(Wagon, on_delete=models.CASCADE, related_name='seats')
    seat_label = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=25.00)

    class Meta:
        db_table = 'seats'

    def __str__(self):
        return f"Seat {self.seat_label} (Wagon {self.wagon.wagon_number})"

class Passenger(models.Model):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    personal_id = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'passengers'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.personal_id})"

class Booking(models.Model):
    # Link booking to the logged-in user (optional, can be null for guests)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_bookings')
    ticket_code = models.CharField(max_length=50, unique=True)
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='bookings')
    departure_city = models.CharField(max_length=100)
    arrival_city = models.CharField(max_length=100)
    departure_date = models.CharField(max_length=50)
    departure_time = models.CharField(max_length=20)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, default="active")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'bookings'

    def __str__(self):
        return f"Booking {self.ticket_code} - {self.status}"

class Ticket(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='tickets')
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name='tickets')
    seat = models.ForeignKey(Seat, on_delete=models.SET_NULL, null=True, blank=True)
    carriage_number = models.CharField(max_length=50, blank=True, null=True)
    seat_number = models.CharField(max_length=20, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'tickets'

    def __str__(self):
        return f"Ticket {self.id} for {self.passenger.first_name} - Seat {self.seat_number}"

class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="completed")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'payments'

    def __str__(self):
        return f"Payment {self.amount} GEL for {self.booking.ticket_code}"