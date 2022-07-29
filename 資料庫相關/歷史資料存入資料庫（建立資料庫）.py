import numpy as np
import pandas as pd
import pymysql
from sqlalchemy import create_engine

"""
把整理過後的台灣指數資料放進資料庫（已不需再執行），後面註解內容為資料庫操作（建立資料庫及表）。
"""

TW0050_df = pd.read_csv('./台灣指數資料.csv')
TW0050_df['日期'] = pd.to_datetime(TW0050_df['日期'])
TW0050_df.rename(columns={'日期':'Date'}, inplace=True)
# print(TW0050_df)

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

TW0050_df.to_sql(TableName, con, if_exists='replace', index=False)

cursorInsatnce.execute(sqlQuery)

df = pd.DataFrame(cursorInsatnce.fetchall())    
# print(df)

db.close()




# connectionInstance          = pymysql.connect(host=databaseServerIP,
#                                               user=databaseUserName,
#                                               password=databaseUserPassword,
#                                               cursorclass=cusrorType)

# cursorInsatnce              = connectionInstance.cursor()

# newDatabaseName             = "TW0050"      # Name of the database that is to be created

# # 開新的DB
# sqlStatement                = "CREATE DATABASE " + newDatabaseName  

# cursorInsatnce.execute(sqlStatement)

# # 顯示目前使用者
# cursorInsatnce.execute("SELECT CURRENT_USER")

# print(cursorInsatnce.fetchall())

# sqlQuery                    = "SHOW DATABASES"

# cursorInsatnce.execute(sqlQuery)

# databaseList                = cursorInsatnce.fetchall()

# for datatbase in databaseList:
#     print(datatbase)

# # 開新的TABLE
# sqlQuery                    = """CREATE TABLE TW0050 (
#                                      Date  DATE,
#                                      TW0050  FLOAT,
#                                      TW0050TR FLOAT)"""

# cursorInsatnce.execute(sqlQuery)

# sqlQuery                    = "SHOW TABLES"

# cursorInsatnce.execute(sqlQuery)

# tableList                = cursorInsatnce.fetchall()

# for table in tableList:
#     print(table)

# connectionInstance.close()