import datetime

from django.db.models import QuerySet
from django.utils import timezone

from core import models


def get_available_car_bays(date: datetime) -> QuerySet:
    return models.CarBay.objects.exclude(booking__date=date)


def customer_allowed_to_book(date: datetime, plate: str) -> bool:
    return not models.Booking.objects.filter(customer__plate__iexact=plate.strip(), date=date).exists()


def check_advance_booking(date: datetime, hours_in_advance: int = 24) -> bool:
    date = datetime.datetime(date.year, date.month, date.day, tzinfo=datetime.timezone.utc)
    difference = date - timezone.now()
    difference_in_hours = divmod(difference.total_seconds(), 3600)[0]  # 60*60=3600 seconds in an hour
    return difference_in_hours > hours_in_advance
