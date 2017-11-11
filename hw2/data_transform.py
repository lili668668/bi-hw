import const
import sqlite3
import time
import datetime
import rx
from rx import Observable, Observer

# 資料轉換
# 時間轉換成離散資料，以30分鐘為單位，並計算計算車輛的使用率：空車數量 / 總車位數

global conn
conn = sqlite3.connect(const.YOUBIKE_DB_NAME)
c = conn.cursor()

def GetInfo(pre_time):
    end_time = pre_time + 1800
    str_pre_time = datetime.datetime.fromtimestamp(pre_time).strftime('%Y-%m-%d %H:%M:%S')
    str_end_time = datetime.datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')

    select_cleaned_data_sql = 'select * from cleaned_data where time >= ? and time < ?;'
    info = c.execute(select_cleaned_data_sql, (str_pre_time, str_end_time)).fetchall()
    Observable.from_(info) \
            .group_by(lambda item: item[1]) \
            .subscribe(lambda obs: deal_with_by_sno(str_pre_time, obs))

def deal_with_by_sno(pre_time, obs):
    aver = obs.map(lambda item: item[5] / item[3]) \
        .average(lambda num: num)
    Observable.zip(obs, aver, lambda item, av: (pre_time, item[1], av)).subscribe(on_next = lambda entry: c.execute('insert into transformed_data values(?, ?, ?)', entry),
            on_error = lambda error: print(error),
            on_completed = lambda: conn.commit()
            )

def transform():

    drop_transformed_data_sql = 'drop table if exists transformed_data;'
    init_transformed_data_sql = 'create table transformed_data (time, sno, usage real)'

    c.execute(drop_transformed_data_sql)
    c.execute(init_transformed_data_sql)

    first_time = c.execute('select time from cleaned_data order by time limit 1;').fetchall()[0][0]

    pattern = '%Y-%m-%d %H:%M:%S'
    half_hour = 1800
    tmp_time = time.strptime(first_time, pattern)
    format_str = "%Y-%m-%d %H:00:00" if tmp_time.tm_min < 30 else "%Y-%m-%d %H:30:00"
    first_time = time.strftime(format_str, tmp_time)
    first_timestamp = time.mktime(time.strptime(first_time, pattern))

    last_time = c.execute('select time from cleaned_data order by time desc limit 1;').fetchall()[0][0]
    last_timestamp = time.mktime(time.strptime(last_time, pattern)) + 1

    insert_transformed_data_sql = 'insert into transformed_data values(?, ?, ?);'
    Observable.from_(range(int(first_timestamp), int(last_timestamp), half_hour)) \
            .subscribe(lambda pre_time: GetInfo(pre_time))

