import io
from contextlib import redirect_stdout
from pathlib import Path

from airflow.models import TaskInstance
from airflow.models.dag import DAG
from airflow.models.dagbag import DagBag
from airflow.utils import timezone

from tests.utils import AirflowTestCase

DAG_FILE = Path(__file__).absolute().parent.parent.parent / "dags" / "example_bash_operator.py"


class TestDagDefinition(AirflowTestCase):

    def test_dag_definition(self):
        dag = DagBag(dag_folder=DAG_FILE).get_dag("example_bash_operator2")
        self.assertDagDictEqual({
            'this_will_skip': {'run_this_last'},
            'run_after_loop': {'run_this_last'},
            'runme_0': {"run_after_loop"},
            'runme_1': {"run_after_loop"},
            'runme_2': {"run_after_loop"},
            'run_this_last': set(),
            'also_run_this': {'run_this_last'}
        }, dag)


class TestTasks(AirflowTestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.dag: DAG = DagBag(dag_folder=DAG_FILE).get_dag("example_bash_operator2")

    def test_also_run_this_should_display_text(self):

        with redirect_stdout(io.StringIO()) as f:
            task = self.dag.task_dict['also_run_this']
            TaskInstance(task, timezone.utcnow()).run(
                mark_success=False,
                ignore_all_deps=True,
                ignore_ti_state=True,
                test_mode=True
            )
        stdout = f.getvalue()
        assert "EXPECTED_SCRIPT_OUTPUT" in stdout

    # TODO: Add tests for other tasks


class TestDAG(AirflowTestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.dag: DAG = DagBag(dag_folder=DAG_FILE).get_dag("example_bash_operator")

    def test_also_run_this_should_display_text(self):
        self.dag.run()

