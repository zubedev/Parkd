# Park'd
Parking booking API

## Model / Design
- an assumption is made that the API is for a `single` car park that houses `multiple` car bays - in this case: 4 car bays.
- the car bays have unique IDs (`integer`) that are auto generated - e.g. Car Bay `1`, Car Bay `2`, ...
- available car bay for a given date is automatically retrieved instead of manual assignment.
- customers do need to register/signup, instead just enter their `name` and `plate` during booking.
- as a minimum viable api system, no authentication model is integrated - supports the previous assumption.
- lack of any proper `customer` verification or uniqueness, system thereby uses `plate` as identifier for unique a `customer`.
- all-day (`date`) is assumed to be from midnight to midnight. 24 hours advance booking means 24 hours before the midnight (`date`).
- currently the API only accepts `json` data (no `form-data`).

## How to run API
`Docker` is required to run the containerd application - https://docs.docker.com/get-docker/
- copy `.env.base` to `.env`
- run `docker-compose build`
- then `docker-compose up`
- browse to api root url at http://localhost:8000/api/

TL;DR `cp --update .env.base .env && docker-compose up --build --detach`

Logs: `docker-compose logs -f` [app | db]

Admin URL at http://localhost:8000/admin/ - default credentials set in `.env` file
- username: `superuser`
- password: `pass123$`

### API endpoints
- GET `/api/availability/?date=YYYY-MM-DD`
```json
{
    "count": 4,
    "data": [
        1,
        2,
        3,
        4
    ],
    "message": "Successfully retrieved available car bays for date=2022-07-24"
}
```
- GET `/api/bookings/?date=YYYY-MM-DD`
```json
{
    "count": 2,
    "data": [
        {
            "id": "039990af-41b5-4c06-a29c-e3b42e81ee7c",
            "date": "2022-07-23",
            "carbay": 2,
            "customer": {
                "name": "Zubair",
                "plate": "Z12345678"
            },
            "created_at": "2022-07-20T12:38:57.260745+08:00"
        },
        {
            "id": "f9a68dac-0916-45b1-aed8-766f562a0690",
            "date": "2022-07-23",
            "carbay": 1,
            "customer": {
                "name": "Edwards",
                "plate": "E12345678"
            },
            "created_at": "2022-07-20T12:38:40.208292+08:00"
        }
    ],
    "message": "Successfully retrieved 2 bookings for date=2022-07-23"
}
```
- POST `/api/book/`
  - `date`: `YYYY-MM-DD`
  - `customer`:
    - `name`: `string`
    - `plate`: `string`
```json
{
    "date": "2022-07-22",
    "customer": {
        "name": "Zubair",
        "plate": "Z12345678"
    }
}
```
```json
{
    "data": {
        "id": "b4a76610-0a02-4623-a679-0a22231791b6",
        "date": "2022-07-24",
        "carbay": 1,
        "customer": {
            "name": "Zubair",
            "plate": "Z12345678"
        },
        "created_at": "2022-07-20T11:56:33.770697Z"
    },
    "message": "Successfully booked carbay=1 for date=2022-07-24"
}
```
## How to run automated tests
An environment variable is set to signal the initiation of the automated tests
set `RUN_TYPE=TEST` on the docker-compose run:
- `docker-compose build`
- `docker-compose run --rm -e RUN_TYPE=TEST app`

Automated tests can also be run manually via docker exec feature
- `docker-compose up --build --detach`
- `docker exec -it parkd_app bash`
- `python manage.py test`
