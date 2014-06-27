import MySQLdb as mysql
import random as rd

conn = mysql.connect(host='localhost',user='root',passwd='123',port=3306)
cur = conn.cursor()

def saycontent():
        conn.select_db("heytalk")
        cur = conn.cursor()
        sql_str = 'select usi from saycontent;'
        count = cur.execute(sql_str)
        result = cur.fetchmany(count)
        alluser = set(result)
        for i in alluser:
                sql_str = "insert into user (usi,uspwd,usname) values (%s,'123','TestName');"%(i)
                cur.execute(sql_str)
                count -= 1
                print count
        conn.commit()

def interest():
        conn.select_db("heytalk")
        cur = conn.cursor()
        cat_list = [("shop",20),("video",20),("education",20),("news",30),("game",30),("music",500)]
        for i in cat_list:
                for j in range(0,i[1]):
                        in_name = i[0] + "_testname"
                        cur.execute("insert into interest (category,name) values (%s,%s);",(i[0],in_name))
                        print i[0]
        conn.commit()

def userinterest():
        row = 0
        conn.select_db("heytalk")
        cur = conn.cursor()
        count = cur.execute("select usi from user")
        usi_res = cur.fetchmany(count)
        uin_list = [("shop",3),("video",3),("education",3),("news",5),("game",5),("music",20)]
        for i in uin_list:
                count = cur.execute('select id from interest where category = "%s"'%(i[0]))
                inid_res = cur.fetchmany(count)
                for j in usi_res:
                        in_list = []
                        for k in range(0,i[1]):
                                rdnum = rd.choice(inid_res)
                                while(rdnum in in_list):
                                        rdnum = rd.choice(inid_res)
                                in_list.append(rdnum)
                                cur.execute("insert into userinterest (usi,interestid) values (%s,%s);",(j,rdnum))
                                row += 1
                                print row
        conn.commit()
                        

if __name__ == "__main__":
        userinterest()
        
