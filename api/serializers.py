from rest_framework import serializers

from core import models


class CustomerSerializer(serializers.ModelSerializer):
    """ Customer data serializer for multiple API """

    class Meta:
        model = models.Customer
        fields = ['name', 'plate']


class MakeBookingSerializer(serializers.ModelSerializer):
    """ Booking data serializer for MakeBookingAPI """

    class Meta:
        model = models.Booking
        fields = ['id', 'date', 'carbay', 'customer', 'created_at']


class GetBookingsSerializer(MakeBookingSerializer):
    """ Booking data serializer for GetBookingsAPI """
    customer = CustomerSerializer()
