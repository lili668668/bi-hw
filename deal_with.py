import const
import sqlite3
import time
import datetime
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

select_fixed_data_sql = 'select * from fixed_data where sv = 1 and tot != 0;'
insert_cleaned_data_sql = 'insert into cleaned_data values(?, ?, ?, ?, ?, ?);'
info = c.execute(select_fixed_data_sql).fetchall()
Observable.from_(info) \
    .subscribe(on_next = lambda item: c.execute(insert_cleaned_data_sql, item)
            , on_error = lambda e: print(e)
            , on_completed = lambda: conn.commit())

# 資料轉換
# 時間轉換成離散資料，以30分鐘為單位，並計算計算車輛的使用率：空車數量 / 總車位數
# 將不同佔點與不同時間，車輛使用率的資料，轉換成離散資料

def GetInfo(pre_time):
    end_time = pre_time + 1800
    select_cleaned_data_sql = 'select * from cleaned_data where time >= ? and time < ?;'
    info = c.execute(select_cleaned_data_sql, pre_time, end_time).fetchall()
    Observable.from_(info) \
            .group_by(lambda item: item[1]) \
            .map(lambda item: (pre_time, item[1], item[5]/item[3]))
            .average(lambda item: item[2])
            .subscribe(print)


drop_transformed_data_sql = 'drop table if exists transformed_data;'
init_transformed_data_sql = 'create table transformed_data values(time, sno, usage real)'

c.execute(drop_transformed_data_sql)
c.execute(init_transformed_data_sql)

first_time = c.execute('select time from cleaned_data order by time limit 1;').fetchall()[0]

pattern = '%Y-%m-%d %H:%M:%S'
half_hour = 1800
tmp_time = time.strptime(first_time, pattern)
format_str = "%Y-%m-%d %H:00:00" if tmp_time.tm_min < 30 else "%Y-%m-%d %H:30:00"
first_time = time.strftime(format_str, tmp_time)
first_timestamp = time.mktime(time.strptime(first_time, pattern))

last_time = c.execute('select time from cleaned_data order by time desc limit 1;').fetchall()[0]
last_timestamp = time.mktime(time.strptime(last_time, pattern)) + 1

insert_transformed_data_sql = 'insert into transformed_data values(?, ?, ?);'
info = c.execute(select_cleaned_data_sql).fetchall()
Observable.from_(range(first_timestamp, last_timestamp, half_hour)) \
        .subscribe(lambda pre_time: GetInfo(pre_time))

# 維度轉換
# 站點-30分鐘、一小時
# 區域-30分鐘、一小時
