import const
import sqlite3
import rx
from rx import Observable, Observer

global conn
conn = sqlite3.connect(const.YOUBIKE_DB_NAME)
c = conn.cursor()

# Data Cleaning
# 把那個時間點，暫停營運的站去掉
# 把那個時間點，總車位數是零的站去掉

drop_cleaned_data_sql = 'drop table if exists cleaned_data;'
init_cleaned_data_sql = 'create table cleaned_data (time, sno, sv, tot, sbi,  bemp);'

c.execute(drop_cleaned_data_sql)
c.execute(init_cleaned_data_sql)

# 資料轉換
# 時間轉換成離散資料，以30分鐘為單位，並計算計算車輛的使用率：空車數量 / 總車位數
# 將不同佔點與不同時間，車輛使用率的資料，轉換成離散資料

# 維度轉換
# 站點-30分鐘、一小時
# 區域-30分鐘、一小時
