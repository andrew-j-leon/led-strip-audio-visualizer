import shutil
from pathlib import Path
from typing import Any

from pyfakefs import fake_filesystem_unittest
from selection import Selection, load, save
from util import Jsonable


class TestJsonable(Jsonable):
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def to_json(self):
        return {"name": self.name, "age": self.age}

    def __eq__(self, other: Any) -> bool:
        if (isinstance(other, TestJsonable)):
            return self.to_json() == other.to_json()

        return False


class TestSaveAndLoadSettings(fake_filesystem_unittest.TestCase):

    def setUp(self):
        self.setUpPyfakefs()

        self.existent_directory = Path('existent_directory')
        self.existent_directory.mkdir()

        self.non_existent_directory = Path('non_existent_directory')

        self.existent_file = self.existent_directory.joinpath('existent_file')
        self.existent_file.touch()

        JSONABLE_1A = TestJsonable("name_1a", 10)
        JSONABLE_1B = TestJsonable("name_1b", 11)

        JSONABLE_2A = TestJsonable("name_2a", 9493)
        JSONABLE_2B = TestJsonable("name_2b", 9494)

        ITEMS_1 = {"name_1A": JSONABLE_1A, "name_1B": JSONABLE_1B}
        ITEMS_2 = {"name_2A": JSONABLE_2A, "name_2B": JSONABLE_2B}

        self.selection_1 = Selection(ITEMS_1)
        self.selection_2 = Selection(ITEMS_2)

    def tearDown(self):
        shutil.rmtree(str(self.existent_directory), ignore_errors=True)

    def test_saving_in_directory_that_does_not_exist(self):
        with self.assertRaises(FileNotFoundError):
            save(Selection(), self.non_existent_directory)

    def test_saving_to_a_file(self):
        with self.assertRaises(NotADirectoryError):
            save(Selection(), self.existent_file)

    def test_saving_in_directory_with_insufficient_permissions(self):
        self.existent_directory.chmod(0o100)

        with self.assertRaises(PermissionError):
            save(Selection(), self.existent_directory)

    def test_loading_from_directory_that_does_not_exist(self):
        with self.assertRaises(FileNotFoundError):
            load(self.non_existent_directory, TestJsonable)

    def test_loading_from_a_file(self):
        with self.assertRaises(NotADirectoryError):
            load(self.existent_file, TestJsonable)

    def test_loading_from_directory_with_no_save_data(self):
        EMPTY_SELECTION = Selection()
        SELECTION = load(self.existent_directory, TestJsonable)

        self.assertEqual(EMPTY_SELECTION, SELECTION)

    def test_save_once_and_load(self):
        save(self.selection_1, self.existent_directory)

        SELECTION = load(self.existent_directory, TestJsonable)
        self.assertEqual(self.selection_1, SELECTION)

    def test_overwrite_previous_save(self):
        save(self.selection_1, self.existent_directory)
        save(self.selection_2, self.existent_directory)

        SELECTION = load(self.existent_directory, TestJsonable)

        self.assertEqual(SELECTION, self.selection_2)
