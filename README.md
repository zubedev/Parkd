# Park'd
Parking booking system API

## Model / Design
- an assumption is made that the API is for a `single` car park that houses `multiple` car bays - in this case: 4 car bays.
- the car bays have unique IDs (`integer`) that are auto generated - e.g. `Car Bay 1`, `Car Bay 2`, ...
- customers do need to register/signup, instead just enter their `name` and `licence_plate` during booking.
- as a minimum viable api system, no authentication model is integrated - supports the previous assumption.
- it is also assumed a `customer` will not sell/transfer their car to another `customer` thereby using `licence_plate` as identifier for unique `customer`.

## How to run
`Docker` is required to run the containerd application - https://docs.docker.com/get-docker/
- copy `.env.base` to `.env`
- run `docker-compose build`
- then `docker-compose up`

TL;DR `cp --update .env.base .env && docker-compose up --build --detach`

Logs: `docker-compose logs -f` [app | db]
