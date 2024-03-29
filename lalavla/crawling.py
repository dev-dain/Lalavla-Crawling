import os
import sys
import json
import pymysql.cursors
from collections import OrderedDict
from time import sleep
from selenium import webdriver
from lalavla_category import category_list as cat_list

# 크롬드라이버 위치 절대경로로 설정
driver = webdriver.Chrome("web driver 경로")
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
def get_product_info(big_list, mid_list, small_list):
  '''
  category_list : list(String). 해당 상품의 중/소/카테고리 
  /name : String. 상품 이름
  /number : String. 상품 고유번호
  /brand : String. 브랜드 이름
  /img : String (src). 대표 이미지 -> 복수 개일 수 있으므로 변경 필요 
  product_img_list : list(String). 대표 이미지들의 리스트
  /item_img_list : list(String). 상품 설명 본문 이미지들의 리스트
  rate : String. 평점
  review_count : String (**건) 상품의 리뷰 개수
  /is_discount : boolean. 할인 여부
  /origin_price : String (**원). 정상가
  /discount_price : String (**원). 할인 가격
  옵션이 없는 단일 상품의 경우, 옵션 개수를 0개로 할 것인가 1개로 할 것인가
  그리고 옵션 이름 목록과 가격에 그냥 name과 price를 넣어야 하나?
  품절의 경우 옵션 가격은 얼마?
  /option_count : String. 옵션 개수
  /option_name_list : list(String). 옵션별 이름
  /option_price_list : list(String). 옵션별 가격
  option_img_list : list(String). 옵션별 이미지 src
  '''

  sleep(1)
  print(big_list, mid_list, small_list)
  category_list = [big_list, mid_list, small_list]
  ##  name, number, brand  가져오기
  name = (driver.find_element_by_class_name('prd-name')).text
  number = driver.find_element_by_xpath('/html/head/meta[16]').get_attribute('content')
  brand = (driver.find_element_by_class_name('category')).text
  img = (driver.find_element_by_css_selector('#prdImgSwiper > div > img')).get_attribute('src')
  ## product_img_list (대표이미지가 대부분 하나임) --> 필요없을듯

  ## item_img_list 
  item_imgs = (driver.find_elements_by_css_selector('#prdDtlTabImg img'))
  item_img_list = [img.get_attribute('src') for img in item_imgs]
  # 위의 코드 = 밑의 3줄 정규표현식 (연습하기!!!)
  # i = []
  # for i in item_img_list:
  #   item_img_list.append(i.get_attribute('src'))
  #   print(i.get_attribute('src'))

  ## is_discount ~ discount_price 
  discount_price = (driver.find_element_by_class_name('price-last')).text.split('\n')[0]
  # 할인 여부 확인
  try:
    # 할인 상품인 경우 .price-dis 요소가 있음
    origin_price = (driver.find_element_by_class_name('price-dis')).text.split('\n')[0]
    is_discount = True
  except:
    # 할인이 아닌 경우 discount_price가 곧 origin_price / 즉, 어느 경우든 discount_price가 해당 상품의 최종가
    origin_price = discount_price
    is_discount = False

  origin_price = origin_price.replace(',', '')
  discount_price = discount_price.replace(',', '')

  # option_count ~ 끝까지
  option_name_list = []
  option_price_list = []
  sold_out = 0
  option_count = 0 

  try:
    # .top-option을 클릭해야 .optSelectMode 인지 바로 optEditMode인지 확인가능 --> 옵션 선택시 optEditMode로 넘어감
    driver.find_element_by_class_name('top-option').click()
    # 옵션이 많으면 optSelectMode // 단일 옵션인 경우 opt-only-one 라는 클래스가 있음, optEditMode (except로 넘어감)
    try:
      driver.find_element_by_class_name('optSelectMode')
      
      # < 옵션 , 가격 정리 > 
      options_name = driver.find_elements_by_class_name('prd-item > .txt')
      options_price = driver.find_elements_by_class_name('prd-item > .right > .font-num-bold')

      for (name, price) in zip(options_name, options_price):
        option_name_list.append(name.text)
        option_price_list.append(price.text)
      
    except:
      # 단일 옵션인 경우
      # 왜 바로 리스트에 넣으면 글자수만큼 들어갈까.. 이것도 고민해봐야할듯? 
      option_name_list = []
      option_price_list = []
    
      option_count = 0
  except:
    # 제품 자체 품절 -> top-option.click 불가능
    sold_out = 1 

  # 안쓰는 것 : category_list , product_img_list, option_img_list
  data["category_list"] = category_list
  data["name"] = name
  data["number"] = number
  data["brand"] = brand
  data["img"] = img
  # data["product_img_list"] = product_img_list
  data["item_img_list"] = item_img_list
  # data["rate"] = rate
  # data["review_count"] = review_count
  data["is_discount"] = is_discount
  data["origin_price"] = origin_price
  data["discount_price"] = discount_price
  data["option_count"] = option_count
  data["option_name_list"] = option_name_list
  data["option_price_list"] = option_price_list
  # data["option_img_list"] = option_img_list

  # print(small_list)

  # for key in data:
  #   print(key + ': ', data[key])

  # try:
  #   with open(
  #     './data/{0}/{1}/{2}/{3}/{4}.json'.format(big_list, mid_list, small_list, category, number), 
  #     'w', encoding='utf-8') as f:
  #     json.dump(data, f, ensure_ascii=False, indent="\t")
  # except: # 디렉터리가 없을 때만 디렉터리를 만듦
  #   os.makedirs('./data/{0}/{1}/{2}/{3}'.format(big_list, mid_list, small_list, category))

  # # sql문 생성 + insert
  # sqls = []
  # sqls.append("insert into discount(is_discount, discount_price) \
  #   values (%s, %d);" % (is_discount_product(int(discount_price), int(origin_price)), int(discount_price)))

  # #$ category_name 이부분은 어떻게 해야하는지 (임의로 수정했음 -> 괜찮은가..? )
  # # sqls.append("insert into item(item_name, item_brand_id, item_img, item_price, category_name, is_optional, barcode, buy) \
  # #   values ('%s', 1, '%s', %d, '%s', %s, %d, %d);" \
  # #   % (name, img, int(discount_price), category_list[-1], is_optional_product(option_count), 1, 1))
  # # for i in range(len(item_img_list)):
  # #   sqls.append("insert into item_img(item_id, item_img, item_order) \
  # #     values(%d, '%s', %d);" % (1, item_img_list[i], i + 1))
  # sqls.append("insert into item(item_name, item_brand_id, item_img, item_price, is_optional, barcode, buy) \
  #   values ('%s', 1, '%s', %d, '%s', %s, %d, %d);" \
  #   % (name, img, int(discount_price), is_optional_product(option_count), 1, 1))
  # for i in range(len(item_img_list)):
  #   sqls.append("insert into item_img(item_id, item_img, item_order) \
  #     values(%d, '%s', %d);" % (1, item_img_list[i], i + 1))
      
  # #$ 이부분 삭제해도 되는지? (옵션별 이미지 없음!)
  # for l in range(len(product_img_list)):
  #   sqls.append("insert into product_img(item_id, product_img) values(%d, '%s');" % 
  #     (1, product_img_list[l]))

  # # 품절인지 알아내는 로직이 필요
  # if is_optional_product(option_count):
  #   for m in range(option_count):
  #       sqls.append("insert into item_option(item_id, item_option_name, is_soldout) \
  #         values(%d, '%s',  %s);" % (1, option_name_list[i], 'N'))
  
  # execute_sql(sqls)

  driver.back() # 뒤로가기
  sleep(0.5)

  
def load_cat_list():
  for big_list in cat_list: # big_list는 cat_list에 String
    for mid_list in cat_list[big_list]: # mid_list는 String
      driver.get(url+cat_list[big_list][mid_list]['all'])
      driver.implicitly_wait(3)
      # 스크롤을 하지 않으면 not clickable 오류가 뜸
      # 따라서, 매 루프마다 모니터 세로 화면의 절반만큼 스크롤을 내릴 수 있도록
      # scroll_Height를 미리 구해 둠
      scroll_height = 360.2
      
      cats = driver.find_elements_by_class_name('swiper-slide > a')
      # 카테고리 한글 이름이 필요할 경우 cats_name 쓸 것
      cats_name = [cat.text for cat in cats]

      # cat_index로 tiny_list의 몇 번째 카테고리를 클릭할지 정함
      # ex) 전체 / 기초세트 / 스킨,토너 / 로션 / 에센스,세럼,앰플 / ...        
      if cats:
        for cat_index in range(len(cats)):
          items = driver.find_elements_by_class_name('prd-list > ul > li > a')          
          height = driver.execute_script('return (window.innerHeight || document.body.clientHeight)')

          for index in range(len(items)): 
            if cat_index:
              cats = driver.find_elements_by_class_name('swiper-slide > a')
              cats[cat_index].click()
              sleep(0.3)

            items = driver.find_elements_by_class_name('prd-list > ul > li > a')
            height += scroll_height 
            driver.execute_script('window.scrollTo(0, ' + str(height) + ')')
            sleep(0.5)

            items[index].click()
            driver.implicitly_wait(3)

            get_product_info(big_list, mid_list, cats_name[cat_index])
      
      else:
        items = driver.find_elements_by_class_name('prd-list > ul > li > a')
        height = driver.execute_script('return (window.innerHeight || document.body.clientHeight)')

        for index in range(len(items)):
          items = driver.find_elements_by_class_name('prd-list > ul > li > a')
          height += scroll_height 
          driver.execute_script('window.scrollTo(0, ' + str(height) + ')')
          sleep(0.5)

          items[index].click()
          driver.implicitly_wait(3)

          get_product_info(big_list, mid_list, '전체')


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