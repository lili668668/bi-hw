import sqlite3
import const
import os

if os.path.exists(const.YOUBIKE_DB_NAME):
    os.remove(const.YOUBIKE_DB_NAME)

conn = sqlite3.connect(const.YOUBIKE_DB_NAME)

c = conn.cursor()

c.execute('create table raw_data(time, iid, sv, sd, vtyp, sno, sna, sip, tot integer, sbi integer, sarea, mday, lat, lng, ar, sareaen, snaen, aren, nbcnt integer, bemp integer, act)')

conn.commit()

conn.close()
