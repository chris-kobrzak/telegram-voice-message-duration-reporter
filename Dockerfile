FROM ubuntu:20.04

LABEL maintainer="Chris Kobrzak <chris.kobrzak@gmail.com>"

RUN apt update -y
RUN apt install -y python3-pip python3-dev

RUN mkdir -p /srv/www

COPY ./requirements.txt /srv/www/requirements.txt

WORKDIR /srv/www

RUN pip3 install -r requirements.txt

COPY . /srv/www/

ENTRYPOINT [ "python3" ]

CMD [ "app/main.py" ]
