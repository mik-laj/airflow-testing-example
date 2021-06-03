import os
import unittest
from glob import glob
from pathlib import Path

from airflow.models import DagBag

ROOT_FOLDER = Path(__file__).absolute().parent.parent.parent


class TestBasic(unittest.TestCase):
    def test_should_be_importable(self):
        example_dags = list(glob(f"{ROOT_FOLDER}/dags/**.py", recursive=True))
        assert 0 != len(example_dags)

        for filepath in example_dags:
            relative_filepath = os.path.relpath(filepath, ROOT_FOLDER)
            with self.subTest(f"File {relative_filepath} should contain dags"):
                dagbag = DagBag(
                    dag_folder=filepath,
                    include_examples=False,
                )
                assert 0 == len(dagbag.import_errors), f"import_errors={str(dagbag.import_errors)}"
                assert len(dagbag.dag_ids) >= 1