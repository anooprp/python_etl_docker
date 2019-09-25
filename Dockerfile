# VERSION 1.0.1
# AUTHOR: Anoop R
# DESCRIPTION: Basic Python ETL container
# BUILD: 
# SOURCE:

FROM python:3.7-slim


# Never prompts the user for choices on installation/configuration of packages
ENV DEBIAN_FRONTEND noninteractive
ENV TERM linux


# Define en_US.
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_MESSAGES en_US.UTF-8

##Common installation
RUN set -ex \
    && buildDeps=' \
        freetds-dev \
        libkrb5-dev \
        libsasl2-dev \
        libssl-dev \
        libffi-dev \
        libpq-dev \
        git \
    ' \
    && apt-get update -yqq \
    && apt-get upgrade -yqq \
    && apt-get install -yqq --no-install-recommends \
        $buildDeps \
        freetds-bin \
        build-essential \
        default-libmysqlclient-dev \
        apt-utils \
        curl \
        rsync \
        netcat \
        locales \
    && sed -i 's/^# en_US.UTF-8 UTF-8$/en_US.UTF-8 UTF-8/g' /etc/locale.gen \
    && locale-gen \
    && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
    && pip install -U pip setuptools wheel \
    && pip install pytz \
    && pip install pyOpenSSL \
    && pip install ndg-httpsclient \
    && pip install pyasn1 \
    && pip install supervisor \
    && if [ -n "${PYTHON_DEPS}" ]; then pip install ${PYTHON_DEPS}; fi \
    && apt-get purge --auto-remove -yqq $buildDeps \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base



## For keeping instance alive
COPY supervisord.conf /etc/

EXPOSE 22 80


# ETL related config


ARG ETL_HOME=/data/your_loc/
ARG PYTHON_DEPS=""


RUN mkdir -p /data/your_loc/CSV/
RUN useradd -ms /bin/bash -d ${ETL_HOME} your_loc 

## code specific libraries

RUN pip install psycopg2==2.7.7 


COPY script/entrypoint.sh /entrypoint.sh

COPY script/DataLoad.py /data/your_loc/
COPY script/test_DataLoad.py /data/your_loc/

COPY data/discover_events.csv /data/your_loc/CSV/
COPY data/events_test.csv /data/your_loc/CSV/

RUN echo "your_loc:your_loc" | chpasswd && adduser your_loc sudo
RUN chown -R your_loc: ${ETL_HOME}

##setting ENV variable for connecting postgres

ENV POSTGRES_HOST=postgres
ENV POSTGRES_PORT=5432
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_DB=your_loc



EXPOSE 8080 5555 8793

USER your_loc
WORKDIR ${ETL_HOME}
ENTRYPOINT ["/entrypoint.sh"]


CMD ["supervisord", "-n"]
