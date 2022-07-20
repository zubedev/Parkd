from django.urls import path

from api import views


app_name = 'api'

urlpatterns = [
    path('availability/', views.CarBayAvailableAPI.as_view(), name='availability'),
    path('book/', views.BookingCreateAPI.as_view(), name='book'),
]
