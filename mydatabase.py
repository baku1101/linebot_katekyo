# StartからEndの間の他の割り込みはしてはいけない
# -> {usrname}_tmpテーブルがある時はEnd以外受け付けない

# import sqlite3
import datetime
import time
import psycopg2
import os
import sys

url = os.getenv('DATABASE_URL', None)
if url is None:
    print('must set DATABASE_URL')
    sys.exit(1)

con = psycopg2.connect(url)
cur = con.cursor()

def CreateTable(usrname):
    cur.execute("CREATE TABLE IF NOT EXISTS {} (year int, month int, start timestamp, finish timestamp, id serial primary key);".format(usrname))
# primary keyの型はint でなく serial じゃないとauto incrementが適用されないので注意

def DropTable(usrname):
    cur.execute("DROP TABLE IF EXISTS {}".format(usrname))
    con.commit()

def Start(usrname):
    CreateTable(usrname)
    if isExistTable(usrname + '_tmp'):
        return False
    cur.execute("CREATE TABLE {}_tmp(start timestamp)".format(usrname))
    start = datetime.datetime.now()
    cur.execute("INSERT INTO {}_tmp(start) values (%s)".format(usrname), (start,))
    con.commit()
    return True

# 月をまたぐものは未対応
def Finish(usrname):
    if not isExistTable(usrname + '_tmp'):
        return False
    finish = datetime.datetime.now()
    cur.execute("SELECT start FROM {}_tmp".format(usrname))
    start = cur.fetchone()[0]
    cur.execute("INSERT INTO {}(year, month, start, finish) VALUES (%s,%s,%s,%s)".format(usrname), (finish.year, finish.month, start, finish))
    cur.execute("DROP TABLE {}_tmp".format(usrname))
    con.commit()
    return True

def GetTableByMonth(usrname, year, month):
    cur.execute("SELECT * FROM {} WHERE year = {} AND month = {}".format(usrname, year, month))
    l = cur.fetchall()
    return l

def InsertRow(usrname, startStr, finishStr):
    start = datetime.datetime.strptime(startStr , "%Y/%m/%d %H:%M")
    finish = datetime.datetime.strptime(finishStr , "%Y/%m/%d %H:%M")
    cur.execute("INSERT INTO {}(year, month, start, finish) VALUES (%s,%s,%s,%s)".format(usrname), (start.year, start.month, start, finish))
    con.commit()

# 月単位でデータを削除
def DeleteMonthData(usrname, year, month):
    cur.execute("DELETE FROM {} WHERE year = {} AND month = {}".format(usrname, year, month))
    con.commit()

# 直近の1列削除
def DeleteRow(usrname):
    cur.execute("SELECT count(*) FROM {}".format(usrname))
    bottom = cur.fetchone()[0]
    cur.execute("DELETE FROM {} WHERE id = {}".format(usrname, bottom))
    con.commit()

# nameテーブルがあるかどうかを返す(tmpテーブルがあるかの確かめ用)
def isExistTable(name):
    cur.execute("SELECT relname FROM pg_stat_user_tables")
    l = cur.fetchall()
    if ((name,) in l):
        return True
    else:
        return False

def GetSumOfMonth(usrname, year, month):
    cur.execute("SELECT * FROM {} WHERE year = {} AND month = {}".format(usrname, year, month))
    sum_time = datetime.timedelta(0)
    for row in cur.fetchall():
        sum_time += (row[3] - row[2])
    return sum_time

if __name__ == '__main__':
    u = 'name'
    CreateTable(u)
    #Start(u)
    #time.sleep(1)
    #finish(u)
