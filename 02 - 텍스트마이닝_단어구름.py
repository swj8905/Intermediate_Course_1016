from bs4 import BeautifulSoup
import urllib.request as req
import urllib.parse as par

keyword = input("키워드 입력 >> ")
encoded = par.quote(keyword) # 한글 -> 특수한 문자

page_num = 1
output_total = ""
while True:
    url = f"https://www.joongang.co.kr/_CP/496?keyword={encoded}&sort%20=&pageItemId=439&page={page_num}"
    code = req.urlopen(url)
    soup = BeautifulSoup(code, "html.parser")
    title = soup.select("h2.headline a")
    if len(title) == 0: # 끝 페이지까지 크롤링 완료했으면?
        break
    for i in title:
        print("제목 :", i.text.strip())
        print("링크 :", i.attrs["href"])
        code_news = req.urlopen(i.attrs["href"])
        soup_news = BeautifulSoup(code_news, "html.parser")
        content = soup_news.select_one("div#article_body")
        result = content.text.strip().replace("     ", " ").replace("   ", "")
        output_total += result
        print(result)
        print()
    if page_num == 2:
        break
    page_num += 1

# 형태소 분석
from konlpy.tag import Okt
okt = Okt()
nouns_list = okt.nouns(output_total)
print(nouns_list)

# 불용어 제거
nouns_without_stopwords = []
for i in nouns_list:
    if len(i) != 1:
        nouns_without_stopwords.append(i)

# 단어 출현 빈도수 카운트
from collections import Counter
count_result = Counter(nouns_without_stopwords)
print(count_result)

# 이미지 가져오기
import numpy as np
from PIL import Image
image_list = np.array(Image.open("./image.jpg"))

# 이미지 색 뽑아오기
from wordcloud import ImageColorGenerator
image_color = ImageColorGenerator(image_list)

# 단어구름 만들기
from wordcloud import WordCloud
wc = WordCloud(mask=image_list, font_path="./NanumMyeongjoBold.ttf", background_color="white")
wc_result = wc.generate_from_frequencies(count_result)

# 단어구름 띄우기
import matplotlib.pyplot as plt
plt.figure() # 창을 만듦
plt.imshow(wc_result.recolor(color_func=image_color), interpolation="bilinear") # 창 안에 이미지를 띄움
plt.axis("off") # 축 없앰
plt.show() # 실제로 그 창을 화면에 띄움.