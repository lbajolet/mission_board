from python:3.4

RUN apt-get -q update
RUN apt-get -qy install -q vim apache2 libapache2-mod-wsgi-py3 supervisor
ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN mkdir -p /opt/mb
ADD . /opt/mb

RUN pip install -r /opt/mb/requirements.txt

# Configure apache and mod_wsgi
RUN cat /opt/mb/apache2_add.conf >> /etc/apache2/apache2.conf

RUN update-rc.d -f  apache2 remove
RUN chown -R www-data:www-data /opt/mb/src/mission_board

RUN mkdir -p /var/www/mb/static
RUN mkdir -p /mb_media

RUN chown -R www-data: /var/www/mb/
RUN chown -R www-data: /mb_media

RUN chmod 700 -R /mb_media

CMD \
	service apache2 stop && \
	cd /opt/mb/src/mission_board/ && \
	python manage.py collectstatic --noinput && \
	/usr/bin/supervisord
