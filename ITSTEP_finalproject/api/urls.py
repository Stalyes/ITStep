from django.urls import path
from .views import (
    StationListView, TrainSearchView, WagonSeatsView, 
    CreateBookingView, BookingDetailView, CancelBookingView
)

urlpatterns = [
    path('stations/', StationListView.as_view(), name='api_stations'),
    path('trains/search/', TrainSearchView.as_view(), name='api_train_search'),
    path('vagon/<int:wagon_id>', WagonSeatsView.as_view(), name='api_wagon_seats'),
    path('bookings/create/', CreateBookingView.as_view(), name='api_create_booking'),
    path('bookings/<str:code>/', BookingDetailView.as_view(), name='api_booking_detail'),
    path('bookings/<str:code>/cancel/', CancelBookingView.as_view(), name='api_cancel_booking'),
]