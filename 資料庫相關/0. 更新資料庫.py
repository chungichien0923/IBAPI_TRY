import numpy as np
import pandas as pd
import pymysql
from sqlalchemy import create_engine
from glob import glob
import os

"""
看哪幾個月的資料還沒更新，全部下載後執行這個檔案，就可以將資料更新至資料庫。
"""

#### 新資料讀取
def date_trans(date):
    date = date.replace(date[0:3], str(int(date[0:3]) + 1911))
    return date

def get_data_from_file(path):
    month_data = pd.read_csv(path, thousands=",", encoding='big5')
    month_data = month_data.iloc[:,:3]
    month_data['日期'] = pd.to_datetime(month_data['日期'].apply(date_trans))
    month_data.columns = ['Date', 'TW50', 'TW50TR']
    return month_data

def data_need_update():
    TAI50_Pattern = '/Users/chungichien/Downloads/TAI50I*.csv'
    TAI50_file_list = glob(TAI50_Pattern)
    TAI50_file_time_list = []
    for i in TAI50_file_list:
        file_time = pd.to_datetime(os.path.getmtime(i), unit='s')
        TAI50_file_time_list.append(file_time)
    TAI50_file_name_list = list(pd.DataFrame([TAI50_file_time_list, TAI50_file_list]).transpose().sort_values(by=0)[1])

    update_df = pd.DataFrame()
    for name in TAI50_file_name_list:
        month_data = get_data_from_file(name)
        update_df = pd.concat([update_df, month_data])

    return update_df

update_df = data_need_update()
# print(update_df)

#### 連接資料庫、讀取舊資料、新舊資料合併後更新資料庫
databaseServerIP            = "127.0.0.1"   # IP address of the MySQL database server

databaseUserName            = "ibdb"        # User name of the database server

databaseUserPassword        = "api0923"     # Password for the database user

DatabaseName                = "TW0050"      # Name of the database that is to be used

TableName                   = "TW0050"      # Name of the table that is to be used

# port                        = "3306"        # default port to connect to mysql

cusrorType                  = pymysql.cursors.DictCursor


db                          = pymysql.connect(host=databaseServerIP,
                                              user=databaseUserName,
                                              password=databaseUserPassword,
                                              database=DatabaseName,
                                              cursorclass=cusrorType)

cursorInsatnce              = db.cursor()

engine = create_engine(f'mysql+pymysql://{databaseUserName}:{databaseUserPassword}@localhost/{DatabaseName}')
con = engine.connect()

sqlQuery                    = f"SELECT * FROM {TableName}"

data_sql = pd.read_sql(sqlQuery, con, parse_dates=["Date"])
# print(data_sql)

TW0050_df = pd.concat([data_sql, update_df]).drop_duplicates('Date', keep='last', ignore_index=True)
# print(TW0050_df)

TW0050_df.to_sql(TableName, con, if_exists='replace', index=False)

cursorInsatnce.execute(sqlQuery)

df = pd.DataFrame(cursorInsatnce.fetchall())    
# print(df)

db.close()