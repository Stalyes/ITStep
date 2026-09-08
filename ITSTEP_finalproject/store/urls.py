from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('trains', views.trains, name='trains'),
    path('passengers/<int:train_id>', views.passengers_page, name='passengers'),
    path('api/vagon/<int:vagon_id>', views.vagon_seats_ajax, name='vagon_seats_ajax'),
    path('payment', views.payment, name='payment'),
    path('process_payment', views.process_payment, name='process_payment'),
    path('download_ticket', views.download_ticket, name='download_ticket'),
    path('check_ticket', views.check_ticket, name='check_ticket'),
    path('verify_ticket', views.verify_ticket, name='verify_ticket'),
    path('cancel_ticket/<str:ticket_id>', views.cancel_ticket, name='cancel_ticket'),
    
    # Auth URLs
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]