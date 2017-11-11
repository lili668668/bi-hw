import const
import json
import sqlite3
import os
import time
import rx
from rx import Observable, Observer

root_path = './raw_data/'
global raw_json
global conn
conn = sqlite3.connect(const.YOUBIKE_DB_NAME)
c = conn.cursor()

def make_time_from_filename(filename):
    filename = filename.split('/')[-1]
    txtname = filename.replace('.txt', '')
    
    raw_time = txtname.split(',')[0]
    raw_date = txtname.split(',')[1]
    
    tmp_time = time.strptime(raw_time, '%H-%M-%S')
    tmp_date = time.strptime(raw_date, '%m-%d-%Y')

    fin_time = time.strftime('%H:%M:%S', tmp_time)
    fin_date = time.strftime('%Y-%m-%d', tmp_date)

    maked_time = fin_date + " " + fin_time
    return maked_time

def storeToDB(file_path):
    maked_time = make_time_from_filename(file_path)
    with open(file_path, mode='r', encoding='big5') as f:
        read_data = f.read()
        try:
            raw_json = json.loads(read_data)
        except:
            return
    f.closed

    retVal = raw_json["retVal"]

    item = Observable.from_(retVal)
    send_time = Observable.repeat(maked_time)
    send_item = Observable.zip(item, send_time, lambda i, t: (t, i['iid'], i['sv'], i['sd'], i['vtyp'], i['sno'], i['sna'], i['sip'], i['tot'], i['sbi'], i['sarea'], i['mday'], i['lat'], i['lng'], i['ar'], i['sareaen'], i['snaen'], i['aren'], i['nbcnt'], i['bemp'], i['act']))

    insert_sql = 'insert into raw_data values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'

    send_item.subscribe(lambda item: c.execute(insert_sql, item))
    conn.commit()
    print(file_path)

subdirs = os.listdir(root_path)
Observable.from_(subdirs) \
    .map(
        lambda subdir: root_path + subdir
    ) \
    .subscribe(
        lambda path: Observable.from_(os.listdir(path)) \
            .map(lambda filename: path + '/' + filename) \
            .subscribe(lambda full_path: storeToDB(full_path))
    )

