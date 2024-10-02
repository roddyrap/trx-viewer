import argparse
import sys
import pathlib

from PySide6 import QtCore, QtWidgets, QtGui

from trx import TestRun

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

        print("Created title widget")

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

        self.test_info_widget = QtWidgets.QTextBrowser()

        test_view_layout.addWidget(self.test_list_view)
        test_view_layout.addWidget(self.test_info_widget)

        print("Created tests list")

        # Layouts.

        self.widget_layout.addWidget(self.title_label)
        self.widget_layout.addWidget(test_view)

        print("Created layouts")

    def update_test_info(self, new_test_index: int):
        test_data = self.test_run.tests[new_test_index]
        formatted_info = f"""Test duration: {test_data.duration}
Execution ID: {test_data.execution_id}
Test ID: {test_data.test_id}

Computer name: {test_data.computer_name}
Duration: {test_data.duration}

Start Date: {test_data.start_date}
End date: {test_data.end_date}

Test type: {test_data.test_type}
Outcome: {test_data.outcome}"""

        if test_data.output.stdout is not None:
            formatted_info += f"\nStandard Output:\n{test_data.output.stdout.text}"

        if test_data.output.stderr is not None:
            formatted_info += f"\nStandard Output:\n{test_data.output.stderr.text}"

        self.test_info_widget.setText(formatted_info)

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

@QtCore.Slot()
def print_widget(widget: QtWidgets.QWidget):
    print(widget)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("trx_path", type=pathlib.Path)

    args = parser.parse_args()

    print("Parsing TRX")

    test_run = TestRun.from_trx_file(args.trx_path)

    print("Launching QT app")

    app = QtWidgets.QApplication([])

    root = TestViewWidget(test_run)
    root.show()

    sys.exit(app.exec())
