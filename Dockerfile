FROM python:3.13-alpine3.20 AS builder

ENV PYTHONUNBUFFERED=1
# Copy app
WORKDIR /app
COPY . /app

# Create venv
RUN python -m venv /opt/venv
# Enable venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
## Build dependencies
RUN apk add postgresql-dev gcc musl-dev libffi-dev rust cargo
RUN pip install gunicorn psycopg[c]
## App dependencies
RUN apk add git xmlsec gettext
RUN pip install -r requirements.txt

# Compile messages
RUN python manage.py compilemessages

# Collect static files
## Create public dir to store them in
RUN mkdir -p /app/public/static
## Collect them
RUN python manage.py collectstatic --noinput

FROM python:3.13-alpine3.20

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install App dependencies
RUN apk add --no-cache xmlsec gettext
# Copy over the build venv
COPY --from=builder /opt/venv /opt/venv

# Enable the venv globally
ENV PATH="/opt/venv/bin:$PATH"

# Copy over the app again
COPY --from=builder /app .

EXPOSE 7000
CMD ["sh", "docker/run.sh"]
