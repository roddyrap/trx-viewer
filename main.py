import argparse
import sys
import pathlib
import logging

from PySide6 import QtCore, QtWidgets, QtGui, QtSvgWidgets

from trx import TestData, TestRun

class TestInformationWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # The grid layout is weird, so I don't use it. 
        self.widget_layout = QtWidgets.QHBoxLayout(self)

        self.left_column_widget = QtWidgets.QWidget()
        self.left_column_layout = QtWidgets.QVBoxLayout(self.left_column_widget)
        self.widget_layout.addWidget(self.left_column_widget)

        self.right_column_widget = QtWidgets.QWidget()
        self.right_column_layout = QtWidgets.QVBoxLayout(self.right_column_widget)
        self.widget_layout.addWidget(self.right_column_widget)

        self.exec_id_label = QtWidgets.QLabel()
        self.left_column_layout.addWidget(self.exec_id_label)

        self.test_id_label = QtWidgets.QLabel()
        self.left_column_layout.addWidget(self.test_id_label)

        self.test_time = QtWidgets.QLabel()
        self.left_column_layout.addWidget(self.test_time)

        self.outcome_image = QtSvgWidgets.QSvgWidget()
        self.right_column_layout.addWidget(self.outcome_image)

        self.test_date_span = QtWidgets.QLabel()
        self.right_column_layout.addWidget(self.test_date_span)

    def update_test_data(self, test_data: TestData):
        self.exec_id_label.setText(f"Exec ID: {test_data.execution_id}")
        self.test_id_label.setText(f"Test ID: {test_data.test_id}")

        self.test_date_span.setText(f"{test_data.start_date} - {test_data.end_date}")

class TestViewWidget(QtWidgets.QWidget):
    def __init__(self, test_run: TestRun):
        super().__init__()
        self.test_run = test_run

        self.widget_layout = QtWidgets.QVBoxLayout(self)

        # Title.

        self.title_label = QtWidgets.QLabel(f"{test_run.name} ({test_run.id})")
        self.title_label.setAutoFillBackground(True)

        title_palette = QtGui.QPalette()
        title_palette.setColor(self.title_label.foregroundRole(), QtGui.QColor("white"))
        title_palette.setColor(self.title_label.backgroundRole(), QtGui.QColor("green"))

        self.title_label.setPalette(title_palette)

        logging.debug("Created title widget")

        # Tests view.

        test_view = QtWidgets.QWidget()
        test_view_layout = QtWidgets.QHBoxLayout(test_view)

        self.test_list_view = QtWidgets.QWidget()
        test_list_layout = QtWidgets.QVBoxLayout(self.test_list_view)


        self.test_filter = QtWidgets.QLineEdit()
        self.test_filter.returnPressed.connect(self.test_filter_changed)
        test_list_layout.addWidget(self.test_filter)

        self.test_filter_palette = QtGui.QPalette()
        self.test_filter.setPalette(self.test_filter_palette)

        self.tests_list_widget = self.__create_tests_list(test_run)
        self.tests_list_widget.itemSelectionChanged.connect(self.test_selection_changed)
        test_list_layout.addWidget(self.tests_list_widget)

        self.test_info_widget = TestInformationWidget()

        # test_view.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        test_view_layout.addWidget(self.test_list_view)
        test_view_layout.addWidget(self.test_info_widget)
        test_view_layout.setStretch(0, 1)
        test_view_layout.setStretch(1, 1)

        logging.debug("Created tests list")

        # Layouts.

        self.widget_layout.addWidget(self.title_label)
        self.widget_layout.addWidget(test_view)

    def update_test_info(self, new_test_index: int):
        test_data = self.test_run.tests[new_test_index]
        self.test_info_widget.update_test_data(test_data)

    @QtCore.Slot()
    def test_selection_changed(self):
        selected_item = self.tests_list_widget.selectedItems()[0]
        new_test_index = selected_item.data(0x100)

        self.update_test_info(new_test_index)

    def filter_tests(self, test_filter: str) -> bool:
        # Currently the only accepted filters are "passed" and "failed".
        PASSED = "passed"
        FAILED = "failed"

        if test_filter not in [FAILED, PASSED]:
            return False

        return True

    @QtCore.Slot()
    def test_filter_changed(self):
        new_filter = self.test_filter.text()
        filter_success = self.filter_tests(new_filter)

        if filter_success:
            filter_background_color = "lightgreen"
        else:
            filter_background_color = "lightred"

        # self.test_filter_palette.setColor(self.test_filter.foregroundRole(), QtGui.QColor("white"))
        self.test_filter_palette.setColor(self.test_filter.backgroundRole(), QtGui.QColor(filter_background_color))

    @staticmethod
    def __create_tests_list(test_run: TestRun) -> QtWidgets.QListWidget:
        list_widget = QtWidgets.QListWidget()

        for index, test in enumerate(test_run.tests):
            list_item = QtWidgets.QListWidgetItem()
            list_item.setText(test.test_name)
            list_item.setData(0x100, index)

            list_widget.addItem(list_item)

        return list_widget

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("trx_path", type=pathlib.Path)

    args = parser.parse_args()

    logging.debug("Parsing TRX")

    test_run = TestRun.from_trx_file(args.trx_path)

    logging.debug("Launching QT app")

    app = QtWidgets.QApplication([])

    root = TestViewWidget(test_run)
    root.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s) [%(levelname)s] %(name)s: %(message)s', level=logging.DEBUG)
    main()
