import const
import data_transform
import sqlite3
import rx
from rx import Observable, Observer

# Data Cleaning
# 把那個時間點，暫停營運的站去掉
# 把那個時間點，總車位數是零的站去掉

def on_completed():
    conn.commit()
    data_transform.transform()

def clean():
    global conn
    conn = sqlite3.connect(const.YOUBIKE_DB_NAME)
    c = conn.cursor()

    drop_cleaned_data_sql = 'drop table if exists cleaned_data;'
    init_cleaned_data_sql = 'create table cleaned_data (time, sno, sv, tot, sbi,  bemp);'

    c.execute(drop_cleaned_data_sql)
    c.execute(init_cleaned_data_sql)

    select_fixed_data_sql = 'select * from fixed_data where sv = "1" and tot != 0;'
    insert_cleaned_data_sql = 'insert into cleaned_data values(?, ?, ?, ?, ?, ?);'
    info = c.execute(select_fixed_data_sql).fetchall()
    Observable.from_(info) \
        .subscribe(on_next = lambda item: c.execute(insert_cleaned_data_sql, item)
                , on_error = lambda e: print(e)
                , on_completed = lambda: on_completed())


