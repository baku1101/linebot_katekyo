import sqlite3
import datetime
import time

con = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
cur = con.cursor()
usrname = "usr1"
cur.execute("CREATE TABLE {}(year int, month int, start timestamp, end timestamp)".format(usrname))

def Start():
    cur.execute("CREATE TABLE {}_tmp(start timestamp)".format(usrname))
    start = datetime.datetime.now()
    cur.execute("INSERT INTO {}_tmp(start) values (?)".format(usrname), (start,))

# 月をまたぐものは未対応
def End():
    end = datetime.datetime.now()
    cur.execute("SELECT start FROM {}_tmp".format(usrname))
    start = cur.fetchone()[0]
    cur.execute("INSERT INTO {}(year, month, start, end) VALUES (?,?,?,?)".format(usrname), (start.year, start.month, start, end))
    cur.execute("DROP TABLE {}_tmp".format(usrname))

def PrintTable(year, month):
    cur.execute("SELECT * FROM {} WHERE year = {} AND month = {}".format(usrname, year, month))
    for row in cur.fetchall():
        print(row)

def SumTimeMonth(year, month):
    cur.execute("SELECT * FROM {} WHERE year = {} AND month = {}".format(usrname, year, month))
    sum_time = datetime.timedelta(0)
    for row in cur.fetchall():
        sum_time += (row[3] - row[2])
    print(sum_time)

if __name__ == '__main__':
    Start()
    time.sleep(2)
    End()
    PrintTable(2019, 4)
    SumTimeMonth(2019, 4)

