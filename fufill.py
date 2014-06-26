import MySQLdb as mysql

conn = mysql.connect(host='localhost',user='root',passwd='123',port=3306)
cur = conn.cursor()

conn.select_db("onechat")
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