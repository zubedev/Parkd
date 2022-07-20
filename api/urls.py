from django.urls import path

from api import views


app_name = 'api'

urlpatterns = [
    path('availability/', views.CarBayAvailableAPI.as_view(), name='availability'),
    path('book/', views.MakeBookingAPI.as_view(), name='book'),
    path('bookings/', views.GetBookingsAPI.as_view(), name='bookings'),
]
