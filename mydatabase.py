# StartからEndの間の他の割り込みはしてはいけない
# -> {usrname}_tmpテーブルがある時はEnd以外受け付けない

# import sqlite3
import datetime
import time
import apsw


con = apsw.Connection("database.db")
cur = con.cursor()

def CreateTable(usrname):
    cur.execute("CREATE TABLE IF NOT EXISTS {}(year int, month int, start timestamp, end timestamp)".format(usrname))

def DropTable(usrname):
    cur.execute("DROP TABLE IF EXISTS {}".format(usrname))

def Start(usrname):
    CreateTable(usrname)
    if isExistTable(usrname + '_tmp'):
        return False
    cur.execute("CREATE TABLE {}_tmp(start timestamp)".format(usrname))
    start = datetime.datetime.now()
    cur.execute("INSERT INTO {}_tmp(start) values (?)".format(usrname), (start,))

# 月をまたぐものは未対応
def End(usrname):
    if not isExistTable(usrname + '_tmp'):
        return False
    end = datetime.datetime.now()
    cur.execute("SELECT start FROM {}_tmp".format(usrname))
    start = cur.fetchone()[0]
    cur.execute("INSERT INTO {}(year, month, start, end) VALUES (?,?,?,?)".format(usrname), (start.year, start.month, start, end))
    cur.execute("DROP TABLE {}_tmp".format(usrname))

def GetTableByMonth(usrname, year, month):
    cur.execute("SELECT * FROM {} WHERE year = {} AND month = {}".format(usrname, year, month))
    l = cur.fetchall()
    return l

def InsertRow(startStr, endStr):
    start = datetime.datetime.strptime(startStr , "%Y/%M/%D %H:%M")
    end = datetime.datetime.strptime(endStr , "%Y/%M/%D %H:%M")
    cur.execute("INSERT INTO {}(year, month, start, end) VALUES (?,?,?,?)".format(usrname), (start.year, start.month, start, end))

# 月単位でデータを削除
def DeleteMonthData(usrname, year, month):
    cur.execute("DELETE FROM {} WHERE year = {} AND month = {}".format(usrname, year, month))

# 直近の1列削除
def DeleteRow(usrname):
    cur.execute("SELECT count(*) FROM {}".format(usrname))
    bottom = cur.fetchone()[0]
    cur.execute("DELETE FROM {} LIMIT {}, 1".format(usrname, bottom-1))

# nameテーブルがあるかどうかを返す(tmpテーブルがあるかの確かめ用)
def isExistTable(name):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
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
    print(sum_time)
    return sum_time

if __name__ == '__main__':
    u = 'name'
    CreateTable(u)
    #Start(u)
    #time.sleep(1)
    #End(u)
