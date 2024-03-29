#!/usr/bin/env bash
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

set -euo pipefail

function log() {
  echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $@"
}

cd "${PROJECT_DIR}"
export COMPOSE_FILE="${PROJECT_DIR}/docker-compose.yaml"
mkdir -p ./dags ./logs ./plugins
touch .env
(
  cat .env | grep -v "^AIRFLOW_UID=" | grep -v "^AIRFLOW_GID=" || true
  echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0"
) > .env
log "Starting environment"
docker-compose up -d
log "Waiting for environment to up"
docker-compose ps -q | xargs -n 1 -P 8 ./scripts/wait-for-container.sh
log "Starting tests"
export PYTHONPATH=$(pwd)
pytest e2e_tests
