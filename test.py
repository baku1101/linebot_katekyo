import mydatabase
import datetime

if __name__ == '__main__':
    u = 'usr'
    t = datetime.datetime.now()
    mydatabase.CreateTable(u)
    mydatabase.Start(u)
    mydatabase.End(u)
    mydatabase.InsertRow(u, '2019/4/1 10:00', '2019/4/1 12:00')
    print(mydatabase.GetTableByMonth(u, t.year, t.month))
    mydatabase.DeleteRow(u)
    print(mydatabase.GetTableByMonth(u, t.year, t.month))
    mydatabase.GetSumOfMonth(u, t.year, t.month)
    l = mydatabase.GetTableByMonth(u, t.year, t.month)
    for row in l:
        rd = datetime.datetime(row)
        print(rd.strftime("%Y/%m/%d %H:%M"))
