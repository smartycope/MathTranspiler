from MainWindow import Main
from PyQt5.QtWidgets import QApplication
from sys import argv

if __name__ == "__main__":
    app = QApplication(argv)
    window = Main()
    window.show()
    app.exec()
