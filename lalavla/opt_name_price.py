import os
import sys
import json
import pymysql.cursors
from collections import OrderedDict
from time import sleep
from selenium import webdriver

driver = webdriver.Chrome("C:\\Python38\\chromedriver")
url = 'https://m.lalavla.com/service/products/productDetail.html?prdId=10003882' 
driver.get(url)
driver.implicitly_wait(3)

options_name = driver.find_elements_by_class_name('prd-item > .txt')
options_price = driver.find_elements_by_class_name('prd-item > .right > .font-num-bold')

for (name, price) in zip(options_name, options_price):
  print(name.get_attribute('innerHTML'), price.get_attribute('innerHTML'))

# try:
#   options_price = driver.find_elements_by_class_name('prd-item > .right > .font-num-bold')

# except:

# for option in options:
#   if option: print(option.text)
# driver.execute_script('document.querySelector(".scroll-cont").style.transform="translate(0px, -320px)";')
# for option in options:
#   if option: print(option.text)

driver.quit()