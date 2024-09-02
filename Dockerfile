FROM python:3.11-alpine3.20

ENV PYTHONUNBUFFERED=1
# Copy app
WORKDIR /app
COPY . /app

# Install dependencies
RUN apk add git xmlsec gettext
RUN pip install -r requirements.txt
RUN pip install gunicorn

# Cleanup
RUN apk del git

# Compile messages
RUN python manage.py compilemessages

# Collect static files
## Create public dir to store them in
RUN mkdir -p /app/public/static
## Collect them
RUN python manage.py collectstatic --noinput

EXPOSE 7000
CMD ["sh", "docker/run.sh"]
