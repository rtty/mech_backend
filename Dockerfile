FROM python:3.7

RUN apt-get update
RUN apt-get install -y apache2 apache2-utils libapache2-mod-wsgi-py3

RUN python -m pip install --upgrade pip

ADD ./requirements.txt .
RUN pip install -r requirements.txt 

# configure ssl for apache2
ADD ./apache-config/default-ssl.conf /etc/apache2/sites-available/default-ssl.conf
ADD ./apache-config/000-default.conf /etc/apache2/sites-available/000-default.conf
RUN a2enmod ssl
RUN a2enmod headers
RUN a2enmod rewrite
RUN a2ensite default-ssl

RUN mkdir -p /var/www/html/mech_backend-master

COPY . /var/www/html/mech_backend-master
WORKDIR /var/www/html/mech_backend-master

EXPOSE 80
EXPOSE 443

CMD python manage.py collectstatic --noinput && apache2ctl -D FOREGROUND
