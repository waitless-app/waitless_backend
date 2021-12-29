FROM python:3.9-alpine

ENV PYTHONUNBUFFERED 1d

COPY ./requirements.txt /requirements.txt
#RUN apk update && apk add gcc libc-dev make git libffi-dev openssl-dev python3-dev libxml2-dev libxslt-dev
RUN apk add --update \
  build-base \
  cairo \
  cairo-dev \
  cargo \
  freetype-dev \
  gcc \
  gdk-pixbuf-dev \
  gettext \
  jpeg-dev \
  lcms2-dev \
  libffi-dev \
  musl-dev \
  openjpeg-dev \
  openssl-dev \
  pango-dev \
  poppler-utils \
  postgresql-client \
  postgresql-dev \
  py-cffi \
  python3-dev \
  rust \
  tcl-dev \
  tiff-dev \
  tk-dev \
  zlib-dev
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev
RUN python -m pip install --upgrade pip
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps
RUN apk add --no-cache geos gdal

RUN mkdir /app
WORKDIR  /app
COPY ./app /app

RUN adduser -D user
USER user


