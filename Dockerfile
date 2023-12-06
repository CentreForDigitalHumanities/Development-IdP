# syntax=docker/dockerfile:1

# Setup
FROM python:3.11-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /

# Dirs
RUN mkdir -p /source
RUN mkdir -p /persistent

### Configuration variables

# This determines if the admin account fixture will be loaded.
# When using a persistent setup, you may wish to turn this off
# so the admin password isn't reset with every container restart.
# In such cases, you should probably just overwrite this in your
# docker-compose.yml.
# Other fixtures are reset _every container start_
ENV LOAD_ADMIN_ACCOUNT=1

# Django DB location. When running in Docker we prefer to have
# this in a persistent location.
ENV DJANGO_DB_LOCATION="/persistent/db.sqlite3"

### Apt installations

RUN --mount=type=cache,target=/var/cache/apt
RUN apt update
RUN apt install -y gettext git mariadb-client libmariadb-dev libffi-dev gcc bash xmlsec1

# Get code
WORKDIR /source
COPY . ./

# Pip updates
RUN --mount=type=cache,target=/root/.cache/pip
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Finally
EXPOSE 7000
CMD python manage.py migrate && python manage.py compilemessages && bash load_fixtures.sh && python manage.py runserver 0.0.0.0:7000

# Debug CMD
# Uncomment if you just want to start up and connect a shell later
# CMD sleep 1d
