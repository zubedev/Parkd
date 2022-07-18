FROM python:3.10-slim

WORKDIR /Parkd

# Install build prerequisites for psycopg2
RUN apt-get update && apt-get install --yes gcc libpq-dev

# Update pip and install poetry
RUN pip install --upgrade pip && pip install poetry

# Copy pyproject.toml and poetry.lock file - '*' ensures no crashes if file is missing
COPY ./pyproject.toml ./poetry.lock* ./

# Configure poetry to use system python and install dependencies
RUN poetry config virtualenvs.create false && poetry install

# Copy application code into '/Parkd'
COPY . /Parkd

# Make the entry script executable and run
RUN chmod +x entry.sh
CMD ["./entry.sh"]
