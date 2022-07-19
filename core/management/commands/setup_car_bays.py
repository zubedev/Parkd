from django.core.management.base import BaseCommand
from decouple import config

from core import models


class Command(BaseCommand):
    help = 'Initialization of Parkd project'

    def handle(self, *args, **options):
        setup_car_bays = config('SETUP_CAR_BAYS', default=True, cast=bool)

        if not setup_car_bays:
            self.stdout.write(
                self.style.WARNING('Car bays auto initiation is disabled. Please add car bays from Django admin or set `CAR_BAYS_INIT=True`.')
            )
            return

        required_bays = config('CAR_BAYS', default=4, cast=int)

        existing_bays = models.CarBay.objects.count()

        if existing_bays < required_bays:
            objects = [models.CarBay() for _ in range(required_bays-existing_bays)]
            models.CarBay.objects.bulk_create(objects)
            count = models.CarBay.objects.count()
            self.stdout.write(
                self.style.SUCCESS(f'{count} car bays have been initialized.')
            )

        elif existing_bays == required_bays:
            self.stdout.write(f'Car bays initialization not required. Found {existing_bays} car bays initialized in database.')

        else:  # existing_bays > car_bays
            self.stdout.write(
                self.style.WARNING(f'Car bays initialization stopped. Found {existing_bays} car bays in database. Adjust manually from Django admin.')
            )
