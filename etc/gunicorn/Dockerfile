FROM python:3.8

ARG MODE

COPY ./requirements.txt /tmp/requirements.txt
RUN pip install --requirement /tmp/requirements.txt

COPY ./etc/gunicorn/${MODE}/gunicorn_config.py /tmp/
COPY ./src/jde /src/jde
COPY ./etc/gunicorn/${MODE}/flaskconf.py /src/jde/conf/
WORKDIR /src/jde
CMD ["gunicorn", "-c", "/tmp/gunicorn_config.py", "jde:flaskApp"]
