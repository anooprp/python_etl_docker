#!/usr/bin/env bash

TRY_LOOP="20"


: "${POSTGRES_HOST:="postgres"}"
: "${POSTGRES_PORT:="5432"}"
: "${POSTGRES_USER:="postgres"}"
: "${POSTGRES_PASSWORD:="postgres"}"
: "${POSTGRES_DB:="your_loc"}"


export \
  POSTGRES_HOST \
  POSTGRES_PORT \
  POSTGRES_USER \
  POSTGRES_PASSWORD \
  POSTGRES_DB \


case "$1" in (supervisord)
	echo 'inside loop'
	sleep 50000

esac
