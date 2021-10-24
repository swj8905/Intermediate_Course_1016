# pip install xlsxwriter 설치해주세요!
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, Qt
import math
import sys
import os
from bs4 import BeautifulSoup
import urllib.request as req
import urllib.parse as par
import pandas as pd
from PyQt5.QtCore import QThread, QObject, QDate
from konlpy.tag import Okt
from collections import Counter
import numpy as np
from PIL import Image
from wordcloud import ImageColorGenerator
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

CalUI = "./crawling.ui"


class Worker(QObject):
    crawling_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(bool)
    wordcloud_progress_signal = pyqtSignal(str)
    finish_wordcloud_signal = pyqtSignal(WordCloud)

    def __init__(self):
        QObject.__init__(self, None)
        self.option_excel = False
        self.filename = ""
        self.option_date = False
        self.start_date = ""
        self.end_date = ""
        self.option_num = False
        self.max_crawling_num = -1
        self.option_wordcloud = False

    def WriteExcel(self, df):
        def str_len(str):
            return len(str.encode('utf-8')) - len(str) * 0.5

        # df.to_excel("./{}.xlsx".format(file_name), index=None)   # 이렇게만 하면 column의 너비가 적절하게 조정이 안됩니다. 따라서 아래 코드로 대체하여 column의 너비를 자동으로 조정해줍니다.

        writer = pd.ExcelWriter("./{}.xlsx".format(self.filename), engine='xlsxwriter')
        # df.reset_index(inplace=True)
        df.to_excel(writer, sheet_name="Sheet1", index=None)  # send df to writer
        worksheet = writer.sheets["Sheet1"]  # pull worksheet object
        for idx, col in enumerate(df):  # loop through all columns
            series = df[col]
            if col == "제목":
                len_function = str_len
            elif col == "링크" or col == "날짜/시간":
                len_function = len
            elif col == "본문 내용":
                break
            max_len = max((
                series.astype(str).map(len_function).max(),  # len of largest item
            )) + 1  # adding a little extra space
            worksheet.set_column(idx, idx, max_len)  # set column width
        writer.save()

    def make_wordcloud(self, output):
        self.wordcloud_progress_signal.emit("형태소 분석 중입니다...")
        spliter = Okt()
        nouns = spliter.nouns(output)
        count = Counter(nouns)
        temp = count.copy().keys()
        for i in temp:
            if len(i) == 1:
                del count[i]
        # 단어구름 만들기
        self.wordcloud_progress_signal.emit("단어 구름 만드는 중입니다...")
        wordcloud = WordCloud(font_path="NanumMyeongjoBold.ttf", background_color='white', width=400,
                              height=400).generate_from_frequencies(count)
        self.finish_wordcloud_signal.emit(wordcloud)

    def crawling(self, received_keyword):
        if self.option_num:
            max_crawling_num = self.max_crawling_num
        else:
            max_crawling_num = -1
        encoded = par.quote(received_keyword)  # 한글 -> 특수한 문자
        page_num = 1

        df = pd.DataFrame(columns=["제목", "링크", "날짜/시간", "본문 내용"])
        current_crawling_num = 0
        output_total = ""
        while True:
            if self.option_date:
                # url = "https://news.joins.com/Search/JoongangNews?page={}&Keyword={}&PeriodType=DirectInput&StartSearchDate={}&EndSearchDate={}&SortType=New&SearchCategoryType=JoongangNews".format(
                #     page_num, encoded, self.start_date, self.end_date)
                url = f"https://www.joongang.co.kr/_CP/496?keyword={encoded}&startDate={self.start_date}&endDate={self.end_date}&sfield=all&serviceCode=&srcGrpCd=&accurateWord=&searchin=&stopword=&sort%20=&pageItemId=439&page={page_num}"
            else:
                url = f"https://www.joongang.co.kr/_CP/496?keyword={encoded}&sort%20=&pageItemId=439&page={page_num}"
            code = req.urlopen(url)
            soup = BeautifulSoup(code, "html.parser")
            title = soup.select("ul.story_list h2.headline a")
            date = soup.select("li p.date")
            if len(title) == 0:  # 끝 페이지까지 크롤링 완료했으면?
                break
            for i in range(len(title)):
                code_news = req.urlopen(title[i].attrs["href"])
                soup_news = BeautifulSoup(code_news, "html.parser")
                content = soup_news.select_one("div#article_body")
                content_result = content.text.strip().replace("     ", " ").replace("   ", "")
                if self.option_wordcloud:
                    output_total += content_result
                result = """제목 : {}
링크 : {}
날짜/시간 : {}
{}

                """.format(title[i].text, title[i].attrs["href"], date[i].string, content_result)
                self.crawling_signal.emit(result)

                # 데이터 프레임에 행 추가
                if self.option_excel:
                    df = df.append(
                        pd.DataFrame([[title[i].text, title[i].attrs["href"], date[i].string, content_result]],
                                     columns=["제목", "링크", "날짜/시간", "본문 내용"]))
                current_crawling_num += 1
                if current_crawling_num == max_crawling_num:
                    break
            else:  # 지금은 for ~ else 문을 사용했습니다. for ~ else 문은 for문을 도는 동안 for문 '안'에서 break 를 만나지 않았다면 else 문을 실행되게 만들어줍니다.
                # 이걸 사용한 이유는.. current_crawling_num 이 max_crawling_num과 같아졌을 때, for 문 뿐만 아니라, 더 바깥에 있는 while문 까지 빠져나와야 하는데
                # break 명령어는 현재 속해 있는 반복문 (이 코드에서는 for문!) 밖에 빠져나오지 못하기 때문입니다.
                # 따라서 for ~ else 문과 else 문 바로 밑에 break 를 하나 더 만듦으로써, current_crawling_num 이 max_crawling_num과 같아졌을 때,
                # 한번에 for문과 while 문을 빠져 나오게 만들어준 것입니다.
                page_num += 1
                continue
            break
        if self.option_excel:
            self.WriteExcel(df)
        if self.option_wordcloud:
            self.make_wordcloud(output_total)
        self.progress_signal.emit(True)


class MainDialog(QDialog):
    start_signal = pyqtSignal(str)
    send_valve_popup_signal = pyqtSignal()

    def __init__(self):
        QDialog.__init__(self, None)
        uic.loadUi(CalUI, self)
        self.label_start_date.setText(self.start_date.selectedDate().toString("yyyy-MM-dd"))
        self.label_end_date.setText(self.end_date.selectedDate().toString("yyyy-MM-dd"))
        self.group_excel.setEnabled(False)
        self.group_num.setEnabled(False)
        self.group_date.setEnabled(False)
        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)
        self.layout_wordcloud.addWidget(self.canvas)
        ### 쓰레드로 worker 이어주기
        self.worker = Worker()
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.start()
        #####
        self.pushButton.clicked.connect(self.CrawlingStart)
        self.worker.crawling_signal.connect(self.ShowResult)
        self.start_signal.connect(self.worker.crawling)
        self.option_excel.stateChanged.connect(self.option_excel_check)
        self.option_date.stateChanged.connect(self.option_date_check)
        self.option_num.stateChanged.connect(self.option_num_check)
        self.option_wordcloud.stateChanged.connect(self.option_wordcloud_check)
        self.slider_num.valueChanged.connect(self.setting_num_in_lineEdit)
        self.worker.progress_signal.connect(self.finish_crawling)
        self.send_valve_popup_signal.connect(self.all_clear_window)
        self.start_date.clicked[QDate].connect(self.show_start_date)
        self.end_date.clicked[QDate].connect(self.show_end_date)
        self.worker.wordcloud_progress_signal.connect(self.wordcloud_status.setText)
        self.worker.finish_wordcloud_signal.connect(self.show_wordcloud)

    def show_wordcloud(self, wordcloud):
        # 이미지 띄우기
        ax = self.fig.add_subplot(111)
        self.fig.tight_layout()
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis('off')
        self.canvas.draw()
        self.wordcloud_status.setText("단어 구름 생성 완료!")

    def show_start_date(self, date):
        self.label_start_date.setText(self.start_date.selectedDate().toString("yyyy.MM.dd"))

    def show_end_date(self, date):
        self.label_end_date.setText(self.end_date.selectedDate().toString("yyyy.MM.dd"))

    def all_clear_window(self):
        self.lineEdit_keyword.clear()
        self.textBrowser.clear()
        self.pushButton.setEnabled(True)

    def finish_crawling(self, is_finished):
        if is_finished:
            msg = QMessageBox()
            msg.setWindowTitle("안내")
            msg.setText("크롤링이 완료되었습니다.")
            msg.setStandardButtons(QMessageBox.Ok)
            result = msg.exec_()
            if result == QMessageBox.Ok:
                self.send_valve_popup_signal.emit()

    def setting_num_in_lineEdit(self, value):
        self.lineEdit_num.setText(str(value))

    def option_num_check(self, state):
        self.group_num.setEnabled(state)
        self.worker.option_num = state

    def option_wordcloud_check(self, state):
        self.worker.option_wordcloud = state

    def option_date_check(self, state):
        self.group_date.setEnabled(state)
        self.worker.option_date = state

    def option_excel_check(self, state):
        self.group_excel.setEnabled(state)
        self.worker.option_excel = state

    def CrawlingStart(self):
        self.pushButton.setEnabled(False)
        keyword = self.lineEdit_keyword.text()
        if self.option_excel.isChecked() == True:
            self.worker.filename = self.filename.text()
        if self.option_date.isChecked() == True:
            self.worker.start_date = self.start_date.selectedDate().toString("yyyy-MM-dd")
            self.worker.end_date = self.end_date.selectedDate().toString("yyyy-MM-dd")
        if self.option_num.isChecked() == True:
            self.worker.max_crawling_num = int(self.lineEdit_num.text())

        self.start_signal.emit(keyword)

    def ShowResult(self, result):
        self.textBrowser.append(result)


QApplication.setStyle("fusion")
app = QApplication(sys.argv)
main_dialog = MainDialog()
main_dialog.show()

sys.exit(app.exec_())