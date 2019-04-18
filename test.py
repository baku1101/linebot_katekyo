import mydatabase
import datetime
import os
import time

if __name__ == '__main__':
    u = 'usr'
    t = datetime.datetime.now()
    mydatabase.CreateTable(u)
    if mydatabase.Start(u):
        print("not started")
    if mydatabase.Finish(u):
        print("not finished")
    print("start and finish: ",mydatabase.GetTableByMonth(u, t.year, t.month))
    mydatabase.InsertRow(u, '2019/4/1 10:00', '2019/4/1 12:00')
    print("insert: ",mydatabase.GetTableByMonth(u, t.year, t.month))
    mydatabase.DeleteRow(u)
    print("delete: ",mydatabase.GetTableByMonth(u, t.year, t.month))
    print("sum: ", mydatabase.GetSumOfMonth(u, t.year, t.month))
    l = mydatabase.GetTableByMonth(u, t.year, t.month)
    for row in l:
        start = datetime.datetime.strftime(row[2], "%d日 %H:%M")
        finish = datetime.datetime.strftime(row[3], "%H:%M")
        print(start + ' - ' + finish)
        #rd = datetime.datetime(row)
        #print(rd.strftime("%Y/%m/%d %H:%M"))
