import numpy as np
import MySQLdb as mysql
from datetime import date,datetime

#out_ip = '203.195.138.60'
#in_ip = '10.232.83.107'
#conn = mysql.connect(host = out_ip,user='root',passwd='TengFei12345',port=3306)
conn = mysql.connect(host = 'localhost',user='root',passwd='123',port=3306)
cur = conn.cursor()

def pre_calc_score():
    conn.select_db("heytalk")
    cur = conn.cursor()
    count = cur.execute("select usi,discuss,transmit,time from saycontent")
    row_data = cur.fetchmany(count)
    result = []
    for i in row_data:
        delta = date.today() - i[-1].date()
        rec = [i[0],int(i[1]),int(i[2]),delta.days]
        result.append(rec)
    #[usi,discuss,transmit,days]
    return result

def pre_cluster():
    conn.select_db("heytalk")
    cur = conn.cursor()
    user_count = cur.execute("select usi from user")
    raw_data = cur.fetchmany(user_count)
    usi_list = []
    for i in raw_data:
        usi_list.append(i[0])
    interest_count = cur.execute("select * from userinterest")
    beginid = 1011
    m_interest = np.zeros((user_count,interest_count))
    for i in range(0,len(usi_list)):
        count = cur.execute('select interestid from userinterest where usi = "%s"'%(usi_list[i]))
        ui_res = cur.fetchmany(count)
        for j in ui_res:
            m_interest[i,j[0]-beginid] = 1
    cat_list = [("shop",20),("video",20),("education",20),("news",30),("game",30),("music",500)]
    return usi_list,m_interest,cat_list
        
    
if __name__ == "__main__":
    pre_cluster()
