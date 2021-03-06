'''
올리브영 세부 카테고리에서 1페이지에 있는 상품들의 정보를 가져와
상품 1개씩 순차적으로 data 디렉터리 밑 세부 카테고리 디렉터리에
상품번호.json으로 저장하는 코드
작성자 : github @dev-dain
'''
import os
import sys
import json
import pymysql.cursors
from collections import OrderedDict
from time import sleep
from selenium import webdriver
from lalavla_category import category_list as cat_list

# 크롬드라이버 위치 절대경로로 설정
driver = webdriver.Chrome("C:\\Python38\\chromedriver")
url = 'https://m.lalavla.com/service/products/productCategory.html?CTG_ID='
data = OrderedDict()

truth_table = {'True': 'Y', 'False': 'N'}

def is_optional_product(n):
  return n > 0

def is_discount_product(dis, org):
  return dis != org

def execute_sql(sqls):
  for sql in sqls:
    print(sql)
    cursors.execute(sql)
    conn.commit()

# 대/중/소/카테고리를 넘김
# ex) 스킨케어(big) > 기초스킨케어(mid) > 스킨/토너(small)
def get_product_info(big_list, mid_list, small_list, category):
  '''
  category_list : list(String). 해당 상품의 중/소/카테고리 
  name : String. 상품 이름
  number : String. 상품 고유번호
  brand : String. 브랜드 이름
  img : String (src). 대표 이미지 -> 복수 개일 수 있으므로 변경 필요 
  product_img_list : list(String). 대표 이미지들의 리스트
  item_img_list : list(String). 상품 설명 본문 이미지들의 리스트
  rate : String. 평점
  review_count : String (**건) 상품의 리뷰 개수
  is_discount : boolean. 할인 여부
  origin_price : String (**원). 정상가
  discount_price : String (**원). 할인 가격

  옵션이 없는 단일 상품의 경우, 옵션 개수를 0개로 할 것인가 1개로 할 것인가
  그리고 옵션 이름 목록과 가격에 그냥 name과 price를 넣어야 하나?
  품절의 경우 옵션 가격은 얼마?

  option_count : String. 옵션 개수
  option_name_list : list(String). 옵션별 이름
  option_price_list : list(String). 옵션별 가격
  option_img_list : list(String). 옵션별 이미지 src
  '''

  sleep(1)
  print(big_list, mid_list, small_list)
  

def load_cat_list():
  for big_list in cat_list: # big_list는 cat_list에 String
    for mid_list in cat_list[big_list]: # mid_list는 String
      for small_list in cat_list[big_list][mid_list]: # small_list는 String
        driver.get(url+cat_list[big_list][mid_list][small_list])
        driver.implicitly_wait(3)
        # 스크롤을 하지 않으면 not clickable 오류가 뜸
        # 따라서, 매 루프마다 모니터 세로 화면의 절반만큼 스크롤을 내릴 수 있도록
        # scroll_Height를 미리 구해 둠
        scroll_height = 360.2
        # scroll_height = driver.execute_script('return (window.innerHeight || document.body.clientHeight)')
        # scroll_height //= 2
        cats = driver.find_elements_by_class_name('swiper-slide > a')
        # 카테고리 한글 이름이 필요할 경우 cats_name 쓸 것
        cats_name = [cat.text for cat in cats]

        # cat_index로 tiny_list의 몇 번째 카테고리를 클릭할지 정함
        # ex) 전체 / 기초세트 / 스킨,토너 / 로션 / 에센스,세럼,앰플 / ...        
        for cat_index in range(len(cats)):
          items = driver.find_elements_by_class_name('prd-list > ul > li > a')          
          height = driver.execute_script('return (window.innerHeight || document.body.clientHeight)')
          # height = scroll_height * 2

          for index in range(len(items)): 
            if cat_index:
              cats = driver.find_elements_by_class_name('swiper-slide > a')
              cats[cat_index].click()
              sleep(0.3)
            # print(cat_index, index)       

            items = driver.find_elements_by_class_name('prd-list > ul > li > a')
            height += scroll_height 
            driver.execute_script('window.scrollTo(0, ' + str(height) + ')')
            sleep(0.5)

            items[index].click()
            driver.implicitly_wait(3)

            get_product_info(big_list, mid_list, small_list)

            driver.back()  
            sleep(0.2)


if __name__ == '__main__':
  print('crawling.py main 실행')

  # 이 부분은 DB 정보로 채울 것
  # conn = pymysql.connect(
  #   host = '', # 로컬호스트
  #   user = '',  # 유저
  #   password = '',  # 비밀번호
  #   db = '',  # 데이터베이스
  #   charset = ''  # 인코딩 캐릭터셋
  # )
  # cursors = conn.cursor()
  # print('DB 연동 완료')

  load_cat_list()  
  driver.quit()

else:
  print('crawling.py is imported')