from MainWindow import Main
from PyQt5.QtWidgets import QApplication
from sys import argv
# from Cope import markRoot, debug, ROOT
# markRoot("..")
# debug(ROOT)

if __name__ == "__main__":
    app = QApplication(argv)
    window = Main()
    window.show()
    app.exec()
