ARG AIRFLOW_IMAGE_NAME
FROM ${AIRFLOW_IMAGE_NAME}

COPY ./requirements-test.txt /tmp/requirements-test.txt
RUN pip install --no-cache-dir  --user -r /tmp/requirements-test.txt

USER root
# Cherry-pick: https://github.com/apache/airflow/pull/16231
COPY --chown=airflow:root /celery_executor.py /home/airflow/.local/lib/python3.6/site-packages/airflow/executors/celery_executor.py
USER ${AIRFLOW_UID}
