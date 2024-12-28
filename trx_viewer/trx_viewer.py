import logging
import sys
import argparse
import os

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from .tests_model import TrxListModel

def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("filename", nargs='?')

    args = parser.parse_args()

    model = TrxListModel(args.filename)

    app = QGuiApplication(sys.argv)

    engine = QQmlApplicationEngine()
    engine.setInitialProperties({
        "trxTestsModel": model
    })

    engine.addImportPath(os.path.dirname(os.path.realpath(__file__)))
    engine.loadFromModule("ViewerGUI", "Main")
    if not engine.rootObjects():
        sys.exit(-1)

    exit_code = app.exec()
    del engine

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
