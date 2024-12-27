import logging
import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from PySide6 import QtCore

from trx import TestRun

class TrxListModel(QtCore.QAbstractListModel):
    name_role = QtCore.Qt.UserRole + 1
    index_role = QtCore.Qt.UserRole + 2
    success_role = QtCore.Qt.UserRole + 3

    def __init__(self, trx_filename: str, parent=None):
        super().__init__(parent)

        self.filename = trx_filename
        self.test_run = TestRun.from_trx_file(trx_filename)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        row = index.row()
        if index.isValid() and 0 <= row < self.rowCount():
            if role == TrxListModel.name_role:
                return self.test_run.tests[row].test_name
            elif role == TrxListModel.index_role:
                return row
            elif role == TrxListModel.success_role:
                return self.test_run.tests[row].outcome == "Passed"

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.test_run.tests)

    def roleNames(self):
        return {
            TrxListModel.name_role: b"name",
            TrxListModel.index_role: b"index",
            TrxListModel.success_role: b"success",
        }

    @QtCore.Slot(int, result='QVariant')
    def get(self, row):
        if 0 <= row < self.rowCount():
            return self.test_run.tests[row]

    @QtCore.Slot(int, str, result='QVariant')
    def get_attr(self, row, attribute):
        if 0 <= row < self.rowCount():
            return getattr(self.test_run.tests[row], attribute)

    @QtCore.Slot(int, result='QString')
    def get_formatted_start_date(self, row):
        return self.test_run.tests[row].start_date.strftime("%Y-%m-%d %H:%M:%S")

    @QtCore.Slot(int, result='QString')
    def get_formatted_end_date(self, row):
        return self.test_run.tests[row].end_date.strftime("%Y-%m-%d %H:%M:%S")

    @QtCore.Slot(result='QString')
    def get_test_run_name(self):
        return self.test_run.name

    @QtCore.Slot(result='QString')
    def get_filename(self):
        return self.filename

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_run = TestRun.from_trx_file(sys.argv[1])

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
