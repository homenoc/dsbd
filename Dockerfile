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
ADD Pipfile /opt/app/Pipfile
ADD Pipfile.lock /opt/app/Pipfile.lock
RUN pipenv install --system

ADD manage.py /opt/app/
ADD dsbd/ /opt/app/dsbd/
ADD custom_admin/ /opt/app/custom_admin/
ADD custom_auth/ /opt/app/custom_auth/
ADD ip/ /opt/app/ip/
ADD noc/ /opt/app/noc/
ADD notice/ /opt/app/notice/
ADD router/ /opt/app/router/
ADD service/ /opt/app/service/
ADD ticket/ /opt/app/ticket/


# NGINX
RUN python manage.py collectstatic --noinput
RUN ln -s /opt/app/static /var/www/html/static
ADD files/default.conf /etc/nginx/sites-enabled/default
ADD version.txt /opt/app/version.txt

#EXPOSE 80
EXPOSE 8010

ADD files/entrypoint.sh /opt/app/
CMD ["bash", "-xe", "/opt/app/entrypoint.sh"]
