FROM python:3-slim

LABEL maintainer="Chris Kobrzak <chris.kobrzak@gmail.com>"

RUN mkdir -p /srv/www

COPY ./requirements.txt /srv/www/requirements.txt

WORKDIR /srv/www

RUN pip3 install -r requirements.txt

COPY . /srv/www/

ENTRYPOINT [ "python3" ]

CMD [ "app/main.py" ]
