FROM python:3.13-alpine3.20

ENV PYTHONUNBUFFERED=1
# Copy app
WORKDIR /app
COPY . /app

# Install dependencies
## Container dependencies
RUN apk add postgresql-dev gcc musl-dev libffi-dev
RUN pip install gunicorn psycopg[c]
## App dependencies
RUN apk add git xmlsec gettext
RUN pip install -r requirements.txt

# Cleanup build-only packages
RUN apk del git gcc musl-dev libffi-dev

# Compile messages
RUN python manage.py compilemessages

# Collect static files
## Create public dir to store them in
RUN mkdir -p /app/public/static
## Collect them
RUN python manage.py collectstatic --noinput

EXPOSE 7000
CMD ["sh", "docker/run.sh"]
