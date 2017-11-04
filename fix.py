import const
import sqlite3
import rx
import time
from rx import Observable, Observer

def make_time_from_mday(raw_time):
    tmp_time = time.strptime(raw_time, '%Y%m%d%H%M%S')
    fin_time = time.strftime('%Y-%m-%d %H:%M:%S', tmp_time)
    return fin_time

def fix_data(item):
    ntime = make_time_from_mday(item[11])
    tot = item[9] + item[19]
    return (ntime, item[5], item[2], tot, item[9], item[19])

global conn
conn = sqlite3.connect(const.YOUBIKE_DB_NAME)
c = conn.cursor()

drop_site_sql = 'drop table if exists site;'
init_site_sql = 'create table site(sno, sna, sarea, ar, sareaen, snaen, aren);'
drop_fixed_data_sql = 'drop table if exists fixed_data;'
init_fixed_data_sql = 'create table fixed_data (time, sno, sv, tot, sbi,  bemp);'

c.execute(drop_site_sql)
c.execute(init_site_sql)
c.execute(drop_fixed_data_sql)
c.execute(init_fixed_data_sql)

conn.commit()

insert_site_sql = 'insert into site values(?, ?, ?, ?, ?, ?, ?);'
select_site_info_sql = 'select sno, sna, sarea, ar, sareaen, snaen, aren from raw_data group by sno;'
sites = c.execute(select_site_info_sql).fetchall()
Observable.from_(sites) \
        .subscribe(on_next = lambda item: c.execute(insert_site_sql, item)
                , on_error = lambda e: print(e)
                , on_completed = lambda: conn.commit())



insert_fixed_data_sql = 'insert into fixed_data values(?, ?, ?, ?, ?, ?)'
select_all_sql = 'select * from raw_data;'
all_items = c.execute(select_all_sql).fetchall()
Observable.from_(all_items).map(lambda item: fix_data(item)) \
        .subscribe(on_next = lambda item: c.execute(insert_fixed_data_sql, item),
                on_error = lambda e: print(e),
                on_completed = lambda: conn.commit())
