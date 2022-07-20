from rest_framework import serializers

from core import models


class CustomerSerializer(serializers.ModelSerializer):
    """ Customer data serializer for multiple API """

    class Meta:
        model = models.Customer
        fields = ['name', 'plate']


class BookingSerializer(serializers.ModelSerializer):
    """ Booking data serializer for BookingCreateAPI """

    class Meta:
        model = models.Booking
        fields = ['id', 'date', 'carbay', 'customer', 'created_at']
