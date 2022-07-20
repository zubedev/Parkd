from django.utils import timezone
from rest_framework import exceptions, status, views
from rest_framework.response import Response

from api import serializers
from core import models, utils


class CarBayAvailableAPI(views.APIView):
    """ Available car bay endpoint for given booking date """
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        params = request.query_params

        # validation for `date` field
        date = params.get('date')
        if not date:
            raise exceptions.ValidationError({'message': 'Please provide a date in the url query params /availability/?date=YYYY-MM-DD'})

        # convert `date` string to datetime object
        date = timezone.datetime.strptime(date, '%Y-%m-%d')

        if not date > timezone.now().today():
            raise exceptions.ValidationError({'message': 'Given date must be in the future - e.g. tomorrow\'s date onwards'})

        # car bay availability queryset
        carbays = utils.get_available_car_bays(date)

        response_data = {
            'count': carbays.count(),
            'data': carbays.values_list('id', flat=True),
            'message': f'Successfully retrieved available car bays for date={date.strftime("%Y-%m-%d")}',
        }
        return Response(response_data, status=status.HTTP_200_OK)


class MakeBookingAPI(views.APIView):
    """ Make a booking endpoint for customer """
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        data = request.data

        # pop out the `customer` object and do validations
        customer = data.pop('customer', {})
        if not customer and not customer.get('plate', '') and not customer.get('name', ''):
            raise exceptions.ValidationError({'message': 'Must provide `customer` object with `name` and `plate` values'})

        # check for returning `customer`
        customer_instance = models.Customer.objects.filter(plate__iexact=customer.get('plate').strip()).first()  # or None

        # do some field validations for `customer`
        customer_serializer = serializers.CustomerSerializer(instance=customer_instance, data=customer)
        customer_serializer.is_valid(raise_exception=True)

        # initial partial field validation for `booking`
        booking_serializer = serializers.MakeBookingSerializer(data=data, partial=True)
        booking_serializer.is_valid(raise_exception=True)

        # get the booking date to check if customer can proceed to book (multiple bookings check)
        # then check for advanced notice (24h) then for available car bays for the given booking date
        booking_date = booking_serializer.validated_data.get('date')

        if not utils.customer_allowed_to_book(date=booking_date, plate=customer_serializer.validated_data.get('plate')):
            raise exceptions.ValidationError({'message': 'Only 1 booking allowed per customer per day'})

        if not utils.check_advance_booking(date=booking_date, hours_in_advance=24):  # 24 hours in advance
            raise exceptions.ValidationError({'message': 'Booking must be made 24 hours in advance of booking date'})

        available_car_bays = utils.get_available_car_bays(date=booking_date)
        if not available_car_bays.exists():
            raise exceptions.ValidationError({'message': f'No car bays available for this date: {booking_date}'})
        allocated_car_bay = available_car_bays.order_by('id').first()

        # we can now save the data and finalize the booking
        if not customer_instance:
            customer_serializer.save()

        data = {'customer': customer_serializer.instance.id, 'carbay': allocated_car_bay.id, 'date': booking_date}

        booking_serializer = serializers.MakeBookingSerializer(data=data)
        booking_serializer.is_valid(raise_exception=True)
        booking_serializer.save()

        response_data = {
            'data': {
                'id': booking_serializer.instance.id,
                'date': booking_serializer.instance.date,
                'carbay': booking_serializer.instance.carbay.id,
                'customer': customer_serializer.data,
                'created_at': booking_serializer.instance.created_at
            },
            'message': f'Successfully booked carbay={booking_serializer.instance.carbay.id} '
                       f'for date={booking_serializer.instance.date.strftime("%Y-%m-%d")}',
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class GetBookingsAPI(views.APIView):
    """ API to get booking details for given date """
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        params = request.query_params

        # validation for `date` field
        date = params.get('date')
        if not date:
            raise exceptions.ValidationError({'message': 'Please provide a date in the url query params /bookings/?date=YYYY-MM-DD'})

        # convert `date` string to datetime object
        date = timezone.datetime.strptime(date, '%Y-%m-%d')

        bookings = models.Booking.objects.filter(date=date)
        bookings_data = serializers.GetBookingsSerializer(bookings, many=True).data

        response_message = f'Successfully retrieved {bookings.count()} bookings for date={date.strftime("%Y-%m-%d")}' \
            if bookings.exists() \
            else f'No bookings found for date={date.strftime("%Y-%m-%d")}'

        response_data = {
            'count': bookings.count(),
            'data': bookings_data,
            'message': response_message,
        }
        return Response(response_data, status=status.HTTP_200_OK)
