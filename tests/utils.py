import unittest
from typing import Dict, Set

from airflow.models.dag import DAG


class AirflowTestCase(unittest.TestCase):
    def assertDagDictEqual(self, expected_dag_dict: Dict[str, Set[str]], dag: DAG):
        assert set(dag.task_dict.keys()) == set(expected_dag_dict.keys())

        current_dag_dict = {
            task_id: set(task.downstream_task_ids)
            for task_id, task in dag.task_dict.items()
        }
        assert expected_dag_dict == current_dag_dict
