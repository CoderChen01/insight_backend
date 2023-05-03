FROM python:3.7.6

LABEL version="1.0"

RUN mkdir /project

WORKDIR /project

COPY . /project

# change pip repo
RUN pip3 config set global.index-url http://pypi.douban.com/simple/
RUN pip3 config set install.trusted-host pypi.douban.com
RUN pip3 install -U pip

# install requirements
RUN pip3 install -r requirements.txt \
    && pip3 install uwsgi \
    && pip3 install gevent

EXPOSE 8989

VOLUME /project
