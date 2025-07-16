#!/bin/sh

# Migrate the database
python manage.py migrate

# Check if we should bootstrap
## Can be supressed by setting an env-var NOBOOTSTRAP
if [ -z "$NOBOOTSTRAP" ] && [ "$(python manage.py is_bootstrapped)" = "False" ]; then
    echo "Proceeding with bootstrap..."

    python manage.py loaddata main/fixtures/initial.json

    # Check if we need to bootstrap users as well
    if [ -z "$NOADMINUSERBOOTSTRAP"]; then
        python manage.py loaddata main/fixtures/admin-user.json
    fi
    if [ -z "$NOTESTUSERBOOTSTRAP"]; then
        python manage.py loaddata main/fixtures/surfconext-test-users.json
    fi
fi


# Run da server
exec gunicorn testidp.wsgi:application -c gunicorn.conf.py "$@"
