#!/usr/bin/env bash

set -euo pipefail

function usage() {
CMDNAME="$(basename -- "$0")"

  cat << EOF
Usage: ${CMDNAME} <container_id>

Waits for the container to be in a healthy condition.

EXAMPLE:
$ docker-compose ps -q | xargs -n 1 -P 8 ${CMDNAME}
EOF

}

if [[ "$#" -ne 1 ]]; then
    echo "You must provide a one argument."
    echo
    usage
    exit 1
fi

CONTAINER_ID="$1"

function wait_for_container {
    container_id="$1"
    container_name="$(docker inspect "${container_id}" --format '{{ .Name }}')"
    echo "Waiting for container: ${container_name} [${container_id}]"
    waiting_done="false"
    while [[ "${waiting_done}" != "true" ]]; do
        container_state="$(docker inspect "${container_id}" --format '{{ .State.Status }}')"
        if [[ "${container_state}" == "running" ]]; then
            health_status="$(docker inspect "${container_id}" --format '{{ .State.Health.Status }}')"
            echo "${container_name}: container_state=${container_state}, health_status=${health_status}"
            if [[ ${health_status} == "healthy" ]]; then
                waiting_done="true"
            fi
        else
            echo "${container_name}: container_state=${container_state}"
            waiting_done="true"
        fi
        sleep 1;
    done;
}

if ! docker inspect "${CONTAINER_ID}" &>/dev/null; then
    echo "Container does not exists"
    exit 1
fi

wait_for_container "$CONTAINER_ID"
