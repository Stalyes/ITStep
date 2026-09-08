from rest_framework import serializers
from store.models import Station, Train, Wagon, Seat, Passenger, Booking, Ticket, Payment

class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = '__all__'

class SeatSerializer(serializers.ModelSerializer):
    seatId = serializers.IntegerField(source='id', read_only=True)
    number = serializers.CharField(source='seat_label', read_only=True)
    isOccupied = serializers.SerializerMethodField()

    class Meta:
        model = Seat
        fields = ['id', 'seatId', 'number', 'seat_label', 'price', 'isOccupied']

    def get_isOccupied(self, obj):
        return Ticket.objects.filter(seat=obj, booking__status='active').exists()

class WagonSerializer(serializers.ModelSerializer):
    seats = SeatSerializer(many=True, read_only=True)

    class Meta:
        model = Wagon
        fields = ['id', 'wagon_number', 'wagon_class', 'seats']

class TrainSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()

    class Meta:
        model = Train
        fields = ['id', 'train_number', 'train_name', 'departure_city', 'arrival_city', 'weekday', 'departure_time', 'arrival_time', 'price']

    def get_price(self, obj):
        first_seat = Seat.objects.filter(wagon__train=obj).first()
        return float(first_seat.price) if first_seat else 25.0

class TicketSerializer(serializers.ModelSerializer):
    passenger_name = serializers.CharField(source='passenger.first_name', read_only=True)
    passenger_surname = serializers.CharField(source='passenger.last_name', read_only=True)
    personal_id = serializers.CharField(source='passenger.personal_id', read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'passenger_name', 'passenger_surname', 'personal_id', 'carriage_number', 'seat_number', 'price']

class BookingSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'ticket_code', 'train_id', 'departure_city', 'arrival_city', 'departure_date', 'departure_time', 'total_price', 'status', 'created_at', 'tickets']