from datetime import timedelta

from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status

from core import models, utils


def generate_test_data(count: int = 3, timedelta_days: int = 1):
    booking_date = timezone.now().today() + timedelta(days=timedelta_days)

    customers = ['Alice', 'Bob', 'Charlie', 'Dave', 'Ed']
    for c in customers[:count]:
        customer = models.Customer.objects.create(name=c, plate=f'{c[0]}23456789')
        carbay = utils.get_available_car_bays(booking_date).order_by('id').first()

        if not carbay:
            booking_date += timedelta(days=1)
            carbay = utils.get_available_car_bays(booking_date).order_by('id').first()

        models.Booking.objects.create(date=booking_date, carbay=carbay, customer=customer)


class CarBayAvailabilityAPITests(TestCase):

    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        call_command('setup_car_bays')
        generate_test_data()

    def test_no_given_date(self):
        """
        GIVEN /availability/ api endpoint exists
        WHEN a user makes a get request without providing `date` param
        THEN endpoint returns 400 status code
        AND response message contains user must `provide a date`
        """
        response = self.client.get(reverse('api:availability'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_body = response.json()
        self.assertTrue('provide a date' in response_body['message'])

    def test_invalid_date(self):
        """
        GIVEN /availability/ api endpoint exists
        WHEN a user makes a get request with invalid `date` param
        THEN endpoint returns 400 status code
        AND response message contains `date must be in the future`
        """
        date = timezone.now().today()

        response = self.client.get(reverse('api:availability'), {'date': date.strftime('%Y-%m-%d')})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_body = response.json()
        self.assertTrue('date must be in the future' in response_body['message'])

    def test_valid_date(self):
        """
        GIVEN car bays initialized with test data (3 customers and bookings)
        WHEN a user makes a get request with valid `date` param
        THEN endpoint returns 200 - OK status code
        AND response message contains `Success`
        AND response data is not empty - a bay available
        AND response count equals to 1
        """
        date = timezone.now().today() + timedelta(days=1)

        response = self.client.get(reverse('api:availability'), {'date': date.strftime('%Y-%m-%d')})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_body = response.json()
        self.assertTrue('Success' in response_body['message'])
        self.assertTrue(response_body['data'])  # 1 bays available
        self.assertEqual(response_body['count'], 1)

    def test_valid_date_no_bays_available(self):
        """
        GIVEN car bays initialized with test data (3 customers and bookings)
        WHEN a user makes a get request with valid `date` param
        THEN endpoint returns 200 - OK status code
        AND response message contains `Success`
        AND response data is empty - no bays available
        AND response count equals to 0
        """
        date = timezone.now().today() + timedelta(days=1)
        customer = models.Customer.objects.create(name='Dave', plate='D23456789')
        carbay = utils.get_available_car_bays(date).order_by('id').first()
        models.Booking.objects.create(date=date, carbay=carbay, customer=customer)

        response = self.client.get(reverse('api:availability'), {'date': date.strftime('%Y-%m-%d')})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_body = response.json()
        self.assertTrue('No car bays available' in response_body['message'])
        self.assertFalse(response_body['data'])  # 0 bays available
        self.assertEqual(response_body['count'], 0)


class MakeBookingAPITests(TestCase):

    def setUp(self):
        self.today = timezone.now().today()
        self.today_str = self.today.strftime('%Y-%m-%d')

        self.tomorrow = self.today + timedelta(days=1)
        self.tomorrow_str = self.tomorrow.strftime('%Y-%m-%d')

        self.day_after = self.tomorrow + timedelta(days=1)
        self.day_after_str = self.day_after.strftime('%Y-%m-%d')

        self.customer = {'name': 'Zubair', 'plate': 'Z23456789'}
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        call_command('setup_car_bays')

    def test_invalid_input_customer(self):
        """
        GIVEN car bays initialized with no test data
        WHEN a user makes a post request with invalid `customer` data
        THEN endpoint returns 400 status code
        AND response message contains `Must provide customer object`
        """
        customer_inputs = [{}, {'name': 'Zubair'}, {'plate': 'Z23456789'}]

        for i in customer_inputs:
            data = {'date': self.tomorrow_str, **i}

            response = self.client.post(reverse('api:book'), data, content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            response_body = response.json()
            self.assertTrue('Must provide `customer` object' in response_body['message'])

    def test_invalid_date_advance_booking(self):
        """
        GIVEN car bays initialized with no test data
        WHEN a user makes a post request with invalid `date` value
        THEN endpoint returns 400 status code
        AND response message contains `Must provide customer object`
        """
        data = {'date': self.tomorrow_str, 'customer': self.customer}

        response = self.client.post(reverse('api:book'), data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_body = response.json()
        self.assertTrue('Booking must be made 24 hours in advance' in response_body['message'])

    def test_single_booking_per_customer_per_day(self):
        """
        GIVEN car bays initialized with a single customer
        WHEN same customer tries to make a booking for the same date
        THEN endpoint returns 400 status code
        AND response message contains `Only 1 booking allowed per customer per day`
        """
        # setup the scenario - given:
        customer = models.Customer.objects.create(**self.customer)
        carbay = utils.get_available_car_bays(self.tomorrow).order_by('id').first()
        models.Booking.objects.create(date=self.tomorrow, carbay=carbay, customer=customer)

        data = {'date': self.tomorrow_str, 'customer': self.customer}

        response = self.client.post(reverse('api:book'), data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_body = response.json()
        self.assertTrue('Only 1 booking allowed per customer per day' in response_body['message'])

    def test_no_available_car_bays(self):
        """
        GIVEN car bays initialized with 4 bookings
        WHEN a customer tries to make a booking for the same date
        THEN endpoint returns 400 status code
        AND response message contains `No car bays available`
        """
        # setup the scenario
        generate_test_data(count=4, timedelta_days=2)  # for day after tomorrow

        data = {'date': self.day_after_str, 'customer': self.customer}

        response = self.client.post(reverse('api:book'), data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_body = response.json()
        self.assertTrue('No car bays available' in response_body['message'])

    def test_booking_success_new_customer(self):
        """
        GIVEN car bays initialized with 3 bookings
        WHEN a new customer tries to make a booking for the same date
        THEN endpoint returns 201 - Created status code
        AND response message contains `Success`
        AND bookings count increases to 4
        AND bookings object exists (filtered with date and plate)
        """
        # setup the scenario
        generate_test_data(count=3, timedelta_days=2)  # for day after tomorrow
        self.assertEqual(models.Booking.objects.count(), 3)

        data = {'date': self.day_after_str, 'customer': self.customer}

        response = self.client.post(reverse('api:book'), data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response_body = response.json()
        self.assertTrue('Success' in response_body['message'])
        self.assertEqual(models.Booking.objects.count(), 4)
        self.assertTrue(models.Booking.objects.filter(date=self.day_after_str, customer__plate=self.customer['plate']).exists())


class GetBookingsAPITests(TestCase):

    def setUp(self):
        self.today = timezone.now().today()
        self.today_str = self.today.strftime('%Y-%m-%d')

        self.tomorrow = self.today + timedelta(days=1)
        self.tomorrow_str = self.tomorrow.strftime('%Y-%m-%d')

        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        call_command('setup_car_bays')

    def test_invalid_date(self):
        """
        GIVEN /bookings/ api exists and car bays initialized
        WHEN a user makes a get request without providing `date` param
        THEN endpoint returns 400 status code
        AND response message contains `provide a date`
        """

        response = self.client.get(reverse('api:bookings'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_body = response.json()
        self.assertTrue('provide a date' in response_body['message'])

    def test_valid_date(self):
        """
        GIVEN car bays initialized with test data (3 customers and bookings)
        WHEN a user makes a get request with valid `date` param
        THEN endpoint returns 200 - OK status code
        AND response message contains `Success`
        AND response data is not empty - 3 bookings found
        AND response count equals to 3
        AND booking data contains all details
        """
        # setup the scenario
        generate_test_data()  # for tomorrow

        response = self.client.get(reverse('api:bookings'), {'date': self.tomorrow_str})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_body = response.json()
        self.assertTrue('Success' in response_body['message'])
        self.assertTrue(response_body['data'])  # 3 bookings found
        self.assertEqual(response_body['count'], 3)

        booking_data = response_body['data'][0]
        self.assertTrue(booking_data['id'])
        self.assertTrue(booking_data['carbay'])
        self.assertTrue(booking_data['created_at'])
        self.assertTrue(booking_data['customer']['name'])
        self.assertTrue(booking_data['customer']['plate'])
        self.assertTrue(booking_data['date'])
