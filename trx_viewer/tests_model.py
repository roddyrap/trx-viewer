import logging
from typing import List, Optional
import threading

from PySide6 import QtCore

from .trx import TestRun, StreamedTestMetadata
from .expression_filter import build_filter

class TrxListModel(QtCore.QAbstractListModel):
    name_role = QtCore.Qt.UserRole + 1
    index_role = QtCore.Qt.UserRole + 2
    success_role = QtCore.Qt.UserRole + 3

    def __init__(self, trx_filename: Optional[str], test_load_update_interval = 100_000, parent=None):
        super().__init__(parent)

        self.test_load_update_interval = test_load_update_interval
        self.filename = trx_filename

        self.tests_list: List[TestRun] = []
        self.filtered_tests_list: List[TestRun] = self.tests_list

        self.streamed_tests: Optional[StreamedTestMetadata] = None

        if self.filename is not None:
            self.load_file(self.filename)
        else:
            self.is_loading = False

    @QtCore.Slot(str)
    def load_file(self, filename: str):
        self.tests_list = []
        self.filtered_tests_list = self.tests_list

        self.is_loading = True
        self.filename = filename
        self.streamed_tests = StreamedTestMetadata(self.filename)
        self.test_run_changed.emit()

        test_load_thread = threading.Thread(target=self.load_tests)
        test_load_thread.start()

    def load_tests(self):
        if self.streamed_tests is None:
            return

        for test_index, new_test in enumerate(self.streamed_tests.yield_tests()):
            layout_update = test_index % self.test_load_update_interval == 0
            if layout_update:
                self.layoutAboutToBeChanged.emit()

            self.tests_list.append(new_test)

            if layout_update:
                logging.debug("Currently updating for test: %d", test_index)
                self.layoutChanged.emit()

            test_index += 1

        self.layoutAboutToBeChanged.emit()
        self.layoutChanged.emit()

        self.streamed_tests.close()
        self.is_loading = False
        logging.debug("Done loading tests! (%d)", test_index)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        row = index.row()
        if index.isValid() and 0 <= row < self.rowCount():
            if role == TrxListModel.name_role:
                return self.filtered_tests_list[row].test_name
            elif role == TrxListModel.index_role:
                return row
            elif role == TrxListModel.success_role:
                return self.filtered_tests_list[row].is_success()

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.filtered_tests_list)

    def roleNames(self):
        return {
            TrxListModel.name_role: b"name",
            TrxListModel.index_role: b"index",
            TrxListModel.success_role: b"success",
        }

    @QtCore.Slot(str, result='bool')
    def apply_filter_string(self, filter_str: str):
        logging.debug("Applying filter: %s", filter_str)

        if self.is_loading:
            return False

        if filter_str == "":
            self.filtered_tests_list = self.tests_list
        else:
            filter_function = build_filter(filter_str)
            if filter_function is None:
                return False

            try:
                new_filtered_tests_list = list(filter(lambda x: filter_function(x), self.tests_list))
            except Exception as e:
                logging.warning("Encountered exception while filtering: %s", e)
                return False
            
            self.filtered_tests_list = new_filtered_tests_list

        self.layoutAboutToBeChanged.emit()
        self.layoutChanged.emit()

        return True

    @QtCore.Signal
    def filename_changed(self):
        pass

    def read_filename(self):
        return self._filename

    def set_filename(self, val):
        self._filename = val
        self.filename_changed.emit()

    filename = QtCore. Property(str, read_filename, set_filename, notify=filename_changed)

    @QtCore.Signal
    def test_run_changed(self):
        pass

    def read_test_run_name(self):
        if self.streamed_tests is None:
            return None

        return self.streamed_tests.test_run.name

    test_run_name = QtCore. Property(str, read_test_run_name, notify=test_run_changed)

    @QtCore.Slot(int, result='QVariant')
    def get(self, row):
        if 0 <= row < self.rowCount():
            return self.filtered_tests_list[row]

    @QtCore.Slot(int, str, result='QVariant')
    def get_attr(self, row, attribute):
        if 0 <= row < self.rowCount():
            return getattr(self.filtered_tests_list[row], attribute)

    @QtCore.Slot(int, result='QString')
    def get_formatted_start_date(self, row):
        return self.filtered_tests_list[row].start_date.strftime("%Y-%m-%d %H:%M:%S")

    @QtCore.Slot(int, result='QString')
    def get_formatted_end_date(self, row):
        return self.filtered_tests_list[row].end_date.strftime("%Y-%m-%d %H:%M:%S")

    @QtCore.Slot(result='bool')
    def get_is_loading(self):
        return self.is_loading

    @QtCore.Slot(int, result='QString')
    def get_stdout(self, row):
        return self.filtered_tests_list[row].output.stdout or ""

    @QtCore.Slot(int, result='QString')
    def get_stderr(self, row):
        return self.filtered_tests_list[row].output.stderr or ""
