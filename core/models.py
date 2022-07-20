import uuid

from django.db import models


class TimeStampedModel(models.Model):
    """ An abstract model that records object creation and last updated datetime automatically """
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CarBay(TimeStampedModel):
    """ A model for car bays in the car park """
    id = models.BigAutoField('Car Bay ID', primary_key=True)

    class Meta:
        ordering = ['id']

    def __str__(self) -> str:
        return f'Car Bay {self.id}'

    @property
    def is_available(self) -> bool:
        return self.booking_set.exists()


class Customer(TimeStampedModel):
    """ A model for customers storing information about them """
    id = models.BigAutoField('Customer ID', primary_key=True)
    name = models.CharField('Customer Name', max_length=255)
    plate = models.CharField('Licence Plate', max_length=9, unique=True, db_index=True)

    class Meta:
        ordering = ['name', 'plate']

    def __str__(self) -> str:
        return f'{self.name} <{self.plate}>'


class Booking(TimeStampedModel):
    """ The core booking model for Park'd """
    id = models.UUIDField('Booking ID', primary_key=True, unique=True, default=uuid.uuid4, editable=False, db_index=True)
    carbay = models.ForeignKey(CarBay, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateField('Date Booked', db_index=True)

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=['date', 'carbay'], name='unique_booking'),
        )
        ordering = ['-date', '-created_at']

    def __str__(self) -> str:
        return f'[{self.date}] {self.carbay} - {self.customer}'
