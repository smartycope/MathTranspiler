from MainWindow import Main
from PyQt5.QtWidgets import QApplication
from sys import argv
from Cope import *

displayAllFiles(True)
displayAllFuncs(True)
displayAllLinks(True)

if __name__ == "__main__":
    app = QApplication(argv)
    window = Main()
    window.show()
    app.exec()
