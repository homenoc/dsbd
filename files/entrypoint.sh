#!/bin/bash

/usr/sbin/nginx -g "daemon off;" &

# DB Migration
# Check if update is needed
if ! ./manage.py migrate --check >/dev/null 2>&1; then
  ./manage.py migrate --no-input
  ./manage.py clearsessions
fi

# Create Superuser
if [ "$SKIP_SUPERUSER" == "false" ]; then
  if [ -z ${SUPERUSER_NAME+x} ]; then
    SUPERUSER_NAME='admin'
  fi
  if [ -z ${SUPERUSER_EMAIL+x} ]; then
    SUPERUSER_EMAIL='admin@example.com'
  fi
  if [ -z ${SUPERUSER_PASSWORD+x} ]; then
    SUPERUSER_PASSWORD='test123#'
  fi

  ./manage.py shell --interface python <<END
from django.contrib.auth.models import User
if not User.objects.filter(username='${SUPERUSER_NAME}'):
    u=User.objects.create_superuser('${SUPERUSER_NAME}', '${SUPERUSER_EMAIL}', '${SUPERUSER_PASSWORD}')
END

  echo "Created superuser Username: ${SUPERUSER_NAME}, E-Mail: ${SUPERUSER_EMAIL}"
fi

#python manage.py migrate
gunicorn --bind 0.0.0.0:8000 -w 2 dsbd.wsgi:application