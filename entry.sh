#!/usr/bin/env bash

# Migrate database
printf "\nRunning Django database migrations\n"
python manage.py migrate --no-input

# Collect staticfiles
printf "\nCollecting application staticfiles\n"
python manage.py collectstatic --no-input

# Create superuser for Django admin access
# User exists error ignored (stderr > null)
printf "\nCreating Django admin superuser\n"
python manage.py createsuperuser --no-input 2>/dev/null

# Setup Parkd car bays
printf "\nSetting up Car Bays for Parkd\n"
python manage.py setup_car_bays

# Run development server
printf "\nRunning Django development server\n"
python manage.py runserver 0.0.0.0:8000
