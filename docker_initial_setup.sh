#!/bin/sh

docker compose exec dev-idp python manage.py loaddata main/fixtures/initial.json
docker compose exec dev-idp python manage.py loaddata main/fixtures/admin-user.json
docker compose exec dev-idp python manage.py loaddata main/fixtures/surfconext-test-users.json
