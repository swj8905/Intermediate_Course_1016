from PyQt5.QtWidgets import *
import sys
from PyQt5 import uic

ui_file = "./test.ui"
class MainDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self, None)
        uic.loadUi(ui_file, self)
        self.button.clicked.connect(self.show_text)

    def show_text(self):
        user_input = self.textinput.text()
        self.textinput.clear()
        self.label.setText(user_input)



QApplication.setStyle("fusion")
app = QApplication(sys.argv)
main_dialog = MainDialog()
main_dialog.show()
sys.exit(app.exec_())