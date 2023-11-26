FROM python:3.11.4 AS app

RUN pip install --upgrade pip && pip install pipenv
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates nginx python3-dev xmlsec1 libxmlsec1-dev \
    libldap2-dev libsasl2-dev slapd ldap-utils tox \
    lcov valgrind \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /opt/app
WORKDIR /opt/app

RUN pip install gunicorn daphne

ENV PYTHONPATH=/opt/app/
ADD requirements.txt /opt/app/requirements.txt
RUN pip install -r requirements.txt

ADD manage.py /opt/app/
ADD mgmt/ /opt/app/mgmt/


# NGINX
RUN python manage.py collectstatic --noinput
RUN ln -s /opt/app/static /var/www/html/static
ADD files/default.conf /etc/nginx/sites-enabled/default

#EXPOSE 80
EXPOSE 8010

ADD files/entrypoint.sh /opt/app/
CMD ["bash", "-xe", "/opt/app/entrypoint.sh"]
