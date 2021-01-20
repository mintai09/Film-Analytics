import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
import sys
import os
import math
import time
from datetime import datetime
import xlwt

# 입력 받기
input_title = input('1. 크롤링할 영화 제목을 입력하세요: ')

while(True):
    input_num = input('2. 크롤링할 리뷰 건수는 몇 건입니까?: ')
    try:
        input_num = int(input_num)
        break
    except:
        print('다시 입력해주세요.')
        continue

input_path = input('3. 파일을 저장할 폴더명만 쓰세요: ')

if(input_path == '0'):
    input_path = os.getcwd()

# 웹드라이버 실행
driver = webdriver.Chrome(os.getcwd() + "/chromedriver.exe")
url = 'https://movie.naver.com'
driver.get(url)


# 검색어 입력
search_box =  driver.find_element_by_id('ipt_tx_srch')
search_box.send_keys(input_title)
time.sleep(2)

#검색어 클릭
driver.find_element_by_xpath('//*[@class="auto_tx_area"]/div[1]/ul/li[1]/a').click()
time.sleep(2)

#가장 정확도를 내는 코드 (사용X)
#driver.find_element_by_class_name('btn_srch').click()
#time.sleep(2)

# 검색목록에서 맨 첫번째 영화 클릭
#driver.find_element_by_xpath('//*[@id="old_content"]/ul[2]/li[1]/dl/dt/a').click()
#time.sleep(1)

# 평점
driver.find_element_by_xpath('//*[@id="movieEndTabMenu"]/li[5]/a').click()
time.sleep(1)

# 칼럼 리스트 준비
score = []
text = []
user = []
date = []
good = []
bad = []

# iframe 이동
driver.switch_to_default_content()
driver.switch_to_frame('pointAfterListIframe')

# 전체 소스 가져오기
full_html = driver.page_source
soup = BeautifulSoup(full_html, 'html.parser')


# 전체 글 수를 가져와서 입력받은 건수와 비교
total_comment = soup.find('div', class_='score_total').find('strong',class_='total').em.string
total_comment = int(total_comment.replace(",",""))
print('전체 글 수:',total_comment,'건\n')
if(total_comment < input_num):
    print('입력된 건수가 전체 리뷰 수보다 큽니다. 전체 리뷰 수로 대체합니다.')
    input_num = total_comment

# 크롤링한 글 수 카운트
count = 0

# 각 파일경로와 파일이름 설정
f_txt = input_path + '/' + input_title + '_' + '.txt'
f_csv = input_path + '/' + input_title + '_' + '.csv'
f_xls = input_path + '/' + input_title + '_' + '.xls'

while(True):

    # 리뷰 리스트 가져오기
    content_list =  soup.find('div',class_='ifr_area basic_ifr').find('div', class_ = 'score_result').find('ul').find_all('li')

    for li in content_list:

        count += 1

        # 각 요소 가져오기
        tmp_score = li.find('div', class_='star_score').find('em').text
        tmp_text = li.find('div', class_='score_reple').find('p').text
        tmp_user = li.find('div', class_='score_reple').find('dl').find('span').text
        tmp_date = li.find('div', class_='score_reple').find_all('em')[1].text
        tmp_good = li.find('div', class_='btn_area').find_all('strong')[0].text
        tmp_bad = li.find('div', class_='btn_area').find_all('strong')[1].text

        # 칼럼 리스트에 추가
        score.append(tmp_score)
        text.append(tmp_text)
        user.append(tmp_user)
        date.append(tmp_date)
        good.append(tmp_good)
        bad.append(tmp_bad)

        # 확인용 프린트
        print("총 %s 건 중 %s 번째 리뷰 데이터를 수집합니다===================================="%(input_num, count))
        print('1) 별점:', tmp_score)
        print('2) 리뷰내용:', tmp_text)
        print('3) 작성자:', tmp_user)
        print('4) 작성일자:', tmp_date)
        print('5) 공감:', tmp_good)
        print('6) 비공감:',tmp_bad)
        print('\n')

        # txt파일에 저장
        f = open(f_txt, 'a',encoding='UTF-8')
        f.write("총 %s 건 중 %s 번째 리뷰 데이터를 수집합니다===================================="%(input_num, count) + '\n')
        f.write('1) 별점: ' + tmp_score + '\n')
        f.write('2) 리뷰내용: ' + tmp_text + '\n')
        f.write('3) 작성자: ' + tmp_user + '\n')
        f.write('4) 작성일자: ' + tmp_date + '\n')
        f.write('5) 공감: ' + tmp_good + '\n')
        f.write('6) 비공감: ' + tmp_bad + '\n')
        f.write('\n')

        # 만약 현재 글 수가 입력건수에 도달하면 루프 종료
        if(count == input_num):
            break
    
    if(count == input_num):
        break
    
    # 아직 입력건수에 도달하지 않았다면 다음 페이지를 열고 루프 계속
    else:
        driver.find_element_by_class_name('pg_next').click()
        time.sleep(1)
                
        driver.switch_to_default_content()
        driver.switch_to_frame('pointAfterListIframe')

        full_html = driver.page_source
        soup = BeautifulSoup(full_html, 'html.parser')

# 데이터프레임 생성, 각 칼럼 리스트 넣기   
df = pd.DataFrame()
df['별점'] = score
df['리뷰내용'] = text
df['작성자'] = user
df['작성일자'] = date
df['공감'] = good
df['비공감'] = bad

# 공백 줄바꿈 제거
for i in range(len(df)):
    df['리뷰내용'][i] = df['리뷰내용'][i].replace("\t","")
    df['리뷰내용'][i] = df['리뷰내용'][i].replace("\n","")

# 엑셀과 csv로 저장
df.to_excel(f_xls,encoding="utf-8-sig",index=True)
df.to_csv(f_csv,encoding="utf-8-sig",index=True)

data = pd.read_csv(f'./{input_title}/{input_path}_.csv')
