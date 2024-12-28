import logging
import sys
import threading
from typing import List
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from PySide6 import QtCore

from trx import TestRun, StreamedTestMetadata

class TrxListModel(QtCore.QAbstractListModel):
    name_role = QtCore.Qt.UserRole + 1
    index_role = QtCore.Qt.UserRole + 2
    success_role = QtCore.Qt.UserRole + 3

    def __init__(self, trx_filename: str, test_load_update_interval = 100_000, parent=None):
        super().__init__(parent)

        self.test_load_update_interval = test_load_update_interval
        self.filename = trx_filename
        self.streamed_tests = StreamedTestMetadata(self.filename)
        self.tests_list: List[TestRun] = []

        test_load_thread = threading.Thread(target=self.load_tests)
        test_load_thread.start()

    def load_tests(self):
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
        logging.debug("Done loading tests! (%d)", test_index)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        row = index.row()
        if index.isValid() and 0 <= row < self.rowCount():
            if role == TrxListModel.name_role:
                return self.tests_list[row].test_name
            elif role == TrxListModel.index_role:
                return row
            elif role == TrxListModel.success_role:
                return self.tests_list[row].outcome == "Passed"

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.tests_list)

    def roleNames(self):
        return {
            TrxListModel.name_role: b"name",
            TrxListModel.index_role: b"index",
            TrxListModel.success_role: b"success",
        }

    @QtCore.Slot(int, result='QVariant')
    def get(self, row):
        if 0 <= row < self.rowCount():
            return self.tests_list[row]

    @QtCore.Slot(int, str, result='QVariant')
    def get_attr(self, row, attribute):
        if 0 <= row < self.rowCount():
            return getattr(self.tests_list[row], attribute)

    @QtCore.Slot(int, result='QString')
    def get_formatted_start_date(self, row):
        return self.tests_list[row].start_date.strftime("%Y-%m-%d %H:%M:%S")

    @QtCore.Slot(int, result='QString')
    def get_formatted_end_date(self, row):
        return self.tests_list[row].end_date.strftime("%Y-%m-%d %H:%M:%S")

    @QtCore.Slot(result='QString')
    def get_test_run_name(self):
        return self.streamed_tests.test_run.name

    @QtCore.Slot(result='QString')
    def get_filename(self):
        return self.filename

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    model = TrxListModel(sys.argv[1])

    app = QGuiApplication(sys.argv)

    engine = QQmlApplicationEngine()
    engine.setInitialProperties({
        "trxTestsModel": model
    })

    engine.addImportPath(sys.path[0])
    engine.loadFromModule("ViewerGUI", "Main")
    if not engine.rootObjects():
        sys.exit(-1)

    exit_code = app.exec()
    del engine

    sys.exit(exit_code)
