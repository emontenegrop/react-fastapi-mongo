FROM python:3.11-alpine
USER root

# prevenir escritura de archivos .pyc en el disco
ENV PYTHONDONTWRITEBYTECODE=1

# Salidas a terminal
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=prod
ENV TZ=America/Guayaquil

COPY ./back-files/.compose/local/start.sh /code/start.sh


#COPIAR LAS LIBRERIAS
COPY ./back-files/requirements /tmp/requirements
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --upgrade -r /tmp/requirements/local.txt 

RUN pip install --no-cache-dir --upgrade pip debugpy -t /tmp

COPY ./back-files/app /code/app
COPY ./back-files/pytest.ini /code/pytest.ini

RUN rm -rf /tmp/requirements

RUN apk add curl

RUN chgrp -R 0 /code && \
    chmod -R g=u /code

RUN chmod g+x /code/start.sh

WORKDIR /code
USER 1001

ENTRYPOINT [ "/code/start.sh" ]