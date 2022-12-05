#!/bin/bash

# PURPOSE: used be jenkins to launch Wall_e to the CSSS PROD Discord Guild

set -e -o xtrace
# https://stackoverflow.com/a/5750463/7734535

export COMPOSE_PROJECT_NAME="finance_site"

export prod_container_name="${COMPOSE_PROJECT_NAME}_app"
export prod_container_db_name="${COMPOSE_PROJECT_NAME}_db"
export docker_compose_file="CI/docker-compose.yml"
export compose_project_name=$(echo "$COMPOSE_PROJECT_NAME" | awk '{print tolower($0)}')
export prod_image_name_lower_case=$(echo "$prod_container_name" | awk '{print tolower($0)}')

docker rm -f ${prod_container_name} || true
docker image rm -f ${prod_image_name_lower_case} || true
docker volume create --name="${COMPOSE_PROJECT_NAME}_logs"
docker volume create --name="${COMPOSE_PROJECT_NAME}_receipt_images"
DOCKER="${docker-compose}"
if [ -z ${DOCKER} ]; then
  docker compose -f "${docker_compose_file}" up -d
else
  ${DOCKER} -f "${docker_compose_file}" up -d
fi

sleep 20

container_failed=$(docker ps -a -f name=${prod_container_name} --format "{{.Status}}" | head -1)
container_db_failed=$(docker ps -a -f name=${prod_container_db_name} --format "{{.Status}}" | head -1)

if [[ "${container_failed}" != *"Up"* ]]; then
    docker logs ${prod_container_name}
    exit 1
fi

if [[ "${container_db_failed}" != *"Up"* ]]; then
    docker logs ${prod_container_db_name}
    exit 1
fi
