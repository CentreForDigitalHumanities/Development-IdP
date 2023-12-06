echo "Press ctrl-k to detach..."
docker run -p 7000:7000 -t -i --detach-keys "ctrl-k" django-dev-idp
