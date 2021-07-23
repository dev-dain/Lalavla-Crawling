'''
랄라블라 브랜드를 긁어와서 brand.json으로 저장하는 코드
현재 카테고리 밑에 data를 반드시 만들고 구동하세요
작성자 : github @dev-dain
'''
import os
import sys
import json
from collections import OrderedDict
from time import sleep
from selenium import webdriver

driver = webdriver.Chrome("chrome 웹 드라이버 경로")
url = 'https://m.lalavla.com/service/main/mainBrand.html'
data = OrderedDict()

driver.get(url)
driver.implicitly_wait(5)

# 네비게이션 바에서 ㄱ~ㅎ, ABC까지 하나씩 탭하기
brand_btn_lists = driver.find_elements_by_class_name('nav-brdSrch > li')  # ㄱ~ABC
# brand_btn_lists.insert(0, brand_btn_lists.pop())  # ABC를 앞으로 끌어내기
# print([brand.text for brand in brand_btn_lists])
count = 1 # 전체 브랜드 개수
brand_dict = dict()

# ㄱ~ㅎ, ABC까지 버튼이 ch_btn에 들어감
for i in range(len(brand_btn_lists)):
  brand_btn_lists[i].click()  # 첨자 버튼 클릭
  sleep(0.3)
  driver.implicitly_wait(3)
  # 전체보기 버튼 밑의 브랜드 리스트들
  brand_lists = driver.find_elements_by_class_name('list-brdSrchResult > li a')
  ch_brand_count = len(brand_lists) # 해당 첨자의 브랜드 개수들

  for k in range(ch_brand_count):
    # staleElement 에러 때문에 매번 새로 찾아줘야 함
    brand_lists = driver.find_elements_by_class_name('list-brdSrchResult > li a')
    brand = brand_lists[k]
    driver.implicitly_wait(3)
    b_name = brand.text
    brand.click() # 각 브랜드를 클릭해 들어가기
    driver.implicitly_wait(3)

    try:
      # 브랜드 이미지 찾기
      brand_img = (driver.find_element_by_id("topvisual-image")).get_attribute('src')
      if brand_img == 'http://mimg.lalavla.com/resources':  # 이미지가 없을 경우 except 절로
        raise Exception                  
      brand_dict[b_name] = [count, brand_img]
    except: # 이미지가 없을 경우
      brand_dict[b_name] = [count, "X"]
    
    print(brand_dict)
    count += 1  # 브랜드 1개 찾았으니 count 증가
    driver.back()
    driver.implicitly_wait(3)

  brand_btn_lists = driver.find_elements_by_class_name('nav-brdSrch > li')  # ㄱ~ABC
  driver.implicitly_wait(3)
  
driver.quit()

try:
  with open(
    './data/brand.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent="\t")
except: # 디렉터리가 없을 때만 디렉터리를 만듦
  os.makedirs('./data')

print('done!')