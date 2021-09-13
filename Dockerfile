ARG AIRFLOW_IMAGE_NAME
FROM ${AIRFLOW_IMAGE_NAME}

COPY ./requirements-test.txt /tmp/requirements-test.txt
RUN pip install --no-cache-dir  --user -r /tmp/requirements-test.txt