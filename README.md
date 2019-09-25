# docker-your_loc


docker-compose --version
docker-compose version 1.22.0, build f46880f


## Informations

* Based on Python (3.7-slim) official Image [python:3.7-slim](https://hub.docker.com/_/python/) and uses the official [Postgres](https://hub.docker.com/_/postgres/) as backend
* Install [Docker](https://www.docker.com/)
* Install [Docker Compose](https://docs.docker.com/compose/install/)

## Installation

## Build
Make sure that you are inside the docker-your_loc folder .Then run below command to 
build the image.It will take some time for the first setup 

docker build -t python_etl:latest .


## Usage

After the successful build we need to run docker-compose file .Which includes postgres 9.6
For first time run it will take sometime since postgres need to be downloaded

docker-compose up

used some sample containerID

docker exec -it deeb670a0de7 /bin/bash (python_etl:latest container)

## ETL load command

testing ETL load

python /data/your_loc/test_DataLoad.py -l /data/your_loc/CSV/ -f test.csv 

  

Dataload method can accept multiple parameters .If we need to change the schema we 
can always pass that as input .Details are available in class definition

## checking the loaded data

docker exec -it 63c3c457fa09 /bin/bash (postgres 9.6 )

psql -h localhost -U postgres -d your_loc -W
password :postgres

select COUNT(*) from public.test;

select * from public.fact_test;


