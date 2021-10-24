from PyQt5.QtWidgets import *
import sys
from PyQt5 import uic
from math import *

ui_file = "./calculator.ui"
class MainDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self, None)
        uic.loadUi(ui_file, self)
        self.equalbutton.clicked.connect(self.calculate)

    def calculate(self):
        result = self.inputbox.text()
        math_result = eval(result)
        self.inputbox.clear()
        self.history.append(f"{result}\n= {math_result:,}\n")

QApplication.setStyle("fusion")
app = QApplication(sys.argv)
main_dialog = MainDialog()
main_dialog.show()
sys.exit(app.exec_())