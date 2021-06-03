import unittest
from time import sleep
from typing import Dict, Any, Optional
from urllib.parse import quote_plus
import httpx


import contextlib
import errno
import os
import signal


DEFAULT_TIMEOUT_MESSAGE = os.strerror(errno.ETIME)
DEFAULT_DAG_RUN_TIMEOUT_SEC: int = 5*50


class timeout(contextlib.ContextDecorator):
    def __init__(self, seconds: int, *, timeout_message: str = DEFAULT_TIMEOUT_MESSAGE):
        self.seconds = int(seconds)
        self.timeout_message = timeout_message

    def _timeout_handler(self, signum, frame):
        raise TimeoutError(self.timeout_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self._timeout_handler)
        signal.alarm(self.seconds)

    def __exit__(self, exc_type, exc_val, exc_tb):
        signal.alarm(0)


class AirflowApi:
    """
    Simple Airflow API Client.

    This class is written from scratch to keep the code clear and easy to port to
    another language, e.g. when the team decides to write tests in Java.
    """
    def __init__(self, *, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.username = username
        self.password = password
        self._session = httpx.Client(headers={
            'Content-Type': 'application/json'
        })

    def api_request(self, method: str, path: str, **kwargs):
        response = self._session.request(
            method=method,
            url=f'http://localhost:8080/api/v1/{path.lstrip("/")}', auth=('airflow', 'airflow'), **kwargs
        )
        response.raise_for_status()
        return response

    def get_dag_run(self, dag_id: str, dag_run_id: str) -> Dict[str, Any]:
        return self.api_request(
            method= 'GET', path=f"dags/{quote_plus(dag_id)}/dagRuns/{quote_plus(dag_run_id)}"
        ).json()

    def get_dag(self, dag_id: str) -> Dict[str, Any]:
        return self.api_request(
            method='GET', path=f"dags/{quote_plus(dag_id)}"
        ).json()

    def trigger_dag_run(self, dag_id: str, dag_run_id: Optional[str] = None):
        data = {}
        if dag_run_id is not None:
            data['run_id'] = dag_run_id
        return self.api_request(
            method='POST', path=f"dags/{quote_plus(dag_id)}/dagRuns", json=data
        ).json()

    def patch_dag(self, dag_id: str, is_paused: Optional[bool] = None):
        data = {}
        if is_paused is not None:
            data['is_paused'] = is_paused
        return self.api_request(
            method='PATCH', path=f"dags/{quote_plus(dag_id)}", json=data
        ).json()

    def close(self):
        self._session.close()


class E2ETestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = AirflowApi(
            base_url="htpp://localhost:8080/api/v1",
            username="airflow",
            password="airflow",
        )
        cls.addClassCleanup(cls.client.close)

    def wait_for_dag_run(self, dag_id: str, dag_run_id: str, timeout_sec: int = DEFAULT_DAG_RUN_TIMEOUT_SEC):
        with timeout(timeout_sec):
            while True:
                dag_run_state = self.client.get_dag_run(dag_id, dag_run_id)['state']
                if dag_run_state != "running":
                    break
                sleep(1)

    def run_dag(self, dag_id: str, dag_run_id: Optional[str] = None):
        is_paused = self.client.get_dag(dag_id)['is_paused']
        run_id = self.client.trigger_dag_run(dag_id=dag_id, dag_run_id=dag_run_id)['dag_run_id']
        if is_paused:
            self.client.patch_dag(dag_id=dag_id, is_paused=False)
        self.wait_for_dag_run(dag_id=dag_id, dag_run_id=run_id)
        self.client.patch_dag(dag_id=dag_id, is_paused=is_paused)
        dag_run_state = self.client.get_dag_run(dag_id=dag_id, dag_run_id=run_id)['state']
        assert dag_run_state == "success"
