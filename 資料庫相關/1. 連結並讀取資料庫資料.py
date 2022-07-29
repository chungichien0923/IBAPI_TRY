import numpy as np
import pandas as pd
import pymysql
from sqlalchemy import create_engine

"""
看哪幾個月的資料還沒更新，全部下載後執行這個檔案，就可以將資料更新至資料庫。
"""

#### 連接資料庫、讀取舊資料、新舊資料合併後更新資料庫
databaseServerIP            = "127.0.0.1"   # IP address of the MySQL database server

databaseUserName            = "ibdb"        # User name of the database server

databaseUserPassword        = "api0923"     # Password for the database user

DatabaseName                = "TW0050"      # Name of the database that is to be used

TableName                   = "TW0050"      # Name of the table that is to be used


engine = create_engine(f'mysql+pymysql://{databaseUserName}:{databaseUserPassword}@localhost/{DatabaseName}')
con = engine.connect()

sqlQuery                    = f"SELECT * FROM {TableName}"

data_sql = pd.read_sql(sqlQuery, con, parse_dates=["Date"])
print(data_sql)
# print(data_sql.info())


# #### 檢查資料型態
# cusrorType                  = pymysql.cursors.DictCursor


# db                          = pymysql.connect(host=databaseServerIP,
#                                               user=databaseUserName,
#                                               password=databaseUserPassword,
#                                               database=DatabaseName,
#                                               cursorclass=cusrorType)

# cursorInsatnce              = db.cursor()

# sqlQuery = '''
# SELECT COLUMN_Name ,DATA_TYPE
# FROM INFORMATION_SCHEMA.Columns Where Table_Name = "TW0050"
# '''

# cursorInsatnce.execute(sqlQuery)

# typeList                = cursorInsatnce.fetchall()

# for dtype in typeList:
#     print(dtype)

# cursorInsatnce.close()