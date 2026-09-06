from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from store.models import Station, Train, Wagon, Seat, Booking, Passenger, Ticket, Payment
from .serializers import StationSerializer, TrainSerializer, WagonSerializer, SeatSerializer, BookingSerializer
import random, string

class StationListView(APIView):
    def get(self, request):
        stations = Station.objects.all().order_by('name')
        serializer = StationSerializer(stations, many=True)
        return Response(serializer.data)

class TrainSearchView(APIView):
    def get(self, request):
        src = request.query_params.get('from', '').strip()
        dst = request.query_params.get('to', '').strip()
        day = request.query_params.get('day', '').strip()

        trains = Train.objects.filter(departure_city=src, arrival_city=dst, weekday=day)
        serializer = TrainSerializer(trains, many=True)
        return Response(serializer.data)

class WagonSeatsView(APIView):
    def get(self, request, wagon_id):
        try:
            wagon = Wagon.objects.get(id=wagon_id)
        except Wagon.DoesNotExist:
            return Response({'error': 'Wagon not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = WagonSerializer(wagon)
        return Response(serializer.data)

class CreateBookingView(APIView):
    def post(self, request):
        data = request.data
        train_id = data.get('train_id')
        
        try:
            train = Train.objects.get(id=train_id)
        except Train.DoesNotExist:
            return Response({'error': 'Train not found'}, status=status.HTTP_400_BAD_REQUEST)

        code = 'GEO-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        booking = Booking.objects.create(
            ticket_code=code,
            train=train,
            departure_city=train.departure_city,
            arrival_city=train.arrival_city,
            departure_date=data.get('date', ''),
            departure_time=train.departure_time,
            total_price=0,
            status='active'
        )

        email = data.get('email', '')
        phone = data.get('phone', '')
        total_price = 0

        for p_data in data.get('passengers', []):
            passenger = Passenger.objects.create(
                first_name=p_data.get('first_name'),
                last_name=p_data.get('last_name'),
                personal_id=p_data.get('personal_id'),
                email=email,
                phone=phone
            )

            seat_id = p_data.get('seat_id')
            seat = Seat.objects.filter(id=seat_id).first() if seat_id else None
            price = float(seat.price) if seat else 25.0
            total_price += price

            Ticket.objects.create(
                booking=booking,
                passenger=passenger,
                seat=seat,
                carriage_number=p_data.get('wagon_name', ''),
                seat_number=seat.seat_label if seat else '',
                price=price
            )

        booking.total_price = total_price
        booking.save()

        Payment.objects.create(
            booking=booking,
            amount=total_price,
            status='completed'
        )

        return Response({
            'ticket_code': code,
            'booking_id': booking.id,
            'total': total_price,
            'status': 'active'
        }, status=status.HTTP_201_CREATED)

class BookingDetailView(APIView):
    def get(self, request, code):
        try:
            booking = Booking.objects.get(ticket_code=code)
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = BookingSerializer(booking)
        return Response(serializer.data)

class CancelBookingView(APIView):
    def post(self, request, code):
        try:
            booking = Booking.objects.get(ticket_code=code)
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

        booking.status = 'cancelled'
        booking.save()

        Payment.objects.filter(booking=booking).update(status='refunded')

        return Response({'ticket_code': code, 'status': 'cancelled'})