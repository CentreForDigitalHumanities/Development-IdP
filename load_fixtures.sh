python manage.py loaddata main/fixtures/initial.json

if [[ LOAD_ADMIN_ACCOUNT ]]; then
    python manage.py loaddata main/fixtures/admin-user.json;
fi

python manage.py loaddata main/fixtures/surfconext-test-users.json
