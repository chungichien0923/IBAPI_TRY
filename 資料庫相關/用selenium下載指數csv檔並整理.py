from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

from glob import glob
import os
import time
import random
import numpy as np
import pandas as pd

# 從證交所下載每月台灣五十指數及台灣五十報酬指數CSV檔，然後另行處理

url = 'https://www.twse.com.tw/zh/page/trading/indices/TAI50I.html'
path = '/Users/chungichien/Desktop/chromedriver'

service = Service(path)
options = webdriver.ChromeOptions()

driver = webdriver.Chrome(service=service, options=options)
driver.get(url)
time.sleep(3)
driver.maximize_window()

a = 1
b = 3
time.sleep(random.uniform(a,b))
select_yy = Select(driver.find_element(by=By.NAME, value='yy'))
select_mm = Select(driver.find_element(by=By.NAME, value='mm'))

op_year_list = []
for op in select_yy.options:
    op_year_list.insert(0, op.text)

op_month_list = []
for op in select_mm.options:
    op_month_list.append(op.text)

downloads_counter = 0
for idx, yy in enumerate(op_year_list):
    select_yy.select_by_visible_text(yy)
    time.sleep(random.uniform(a,b))
    
    month_start = 0
    month_end = 12
    if idx == 0:
        month_start = 9
    if idx == (len(op_year_list) - 1):
        month_end = 7   # 視最新月份決定，當時為七月
    
    for mm in op_month_list[month_start:month_end]:
        # print('yy=', yy, 'mm=', mm)
        select_mm.select_by_visible_text(mm)
        time.sleep(random.uniform(a,b))
        driver.find_element(by=By.CSS_SELECTOR, value="a[class='button search']").click()
        time.sleep(random.uniform(a,b)+3)
        driver.find_element(by=By.CSS_SELECTOR, value="a[class='csv']").click()
        time.sleep(random.uniform(a,b)+1.5)
        downloads_counter += 1
    
    time.sleep(random.uniform(5,10))

driver.quit()

def date_trans(date):
    date = date.replace(date[0:3], str(int(date[0:3]) + 1911))
    return date

def get_data_from_file(path):
    month_data = pd.read_csv(path, thousands=",", encoding='big5')
    month_data = month_data.iloc[:,:3]
    month_data['日期'] = pd.to_datetime(month_data['日期'].apply(date_trans))
    TAI50_complete_df.columns = ['Date', 'TW50', 'TW50TR']
    month_data.set_index('Date', inplace=True)
    return month_data

TAI50_Pattern = '/Users/chungichien/Downloads/TAI50I*.csv'
TAI50_file_list = glob(TAI50_Pattern)
TAI50_file_time_list = []
for i in TAI50_file_list:
    file_time = pd.to_datetime(os.path.getmtime(i), unit='s')
    TAI50_file_time_list.append(file_time)
TAI50_file_name_list = list(pd.DataFrame([TAI50_file_time_list, TAI50_file_list]).transpose().sort_values(by=0)[1])

TAI50_complete_df = pd.DataFrame()
for name in TAI50_file_name_list:
    month_data = get_data_from_file(name)
    TAI50_complete_df = pd.concat([TAI50_complete_df, month_data])

TAI50_complete_df.drop(index='2003-11-26').to_csv('./台灣指數資料.csv')