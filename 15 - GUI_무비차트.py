from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
import sys
from PyQt5 import uic
import urllib.request as req
from bs4 import BeautifulSoup

ui_file = "./movie_chart.ui"
class MainDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self, None)
        uic.loadUi(ui_file, self)
        self.button.clicked.connect(self.show_movie_chart)

    def show_movie_chart(self):
        code = req.urlopen("http://www.cgv.co.kr/movies/")
        soup = BeautifulSoup(code, "html.parser")
        title = soup.select("div.sect-movie-chart strong.title")
        img = soup.select("span.thumb-image > img")
        for i in range(len(title)):
            getattr(self, f"text{i+1}").setText(f"{i+1}위. {title[i].string}")
            img_url = img[i].attrs["src"]
            data = req.urlopen(img_url).read() # 이미지 데이터 받아오기
            pixmap = QPixmap() # 이미지를 담을 수 있는 장바구니
            pixmap.loadFromData(data) # 장바구니에 이미지를 넣음
            pixmap = pixmap.scaled(185, 260) # 이미지 사이즈 조절
            getattr(self, f"img{i+1}").setPixmap(pixmap)


QApplication.setStyle("fusion")
app = QApplication(sys.argv)
main_dialog = MainDialog()
main_dialog.show()
sys.exit(app.exec_())