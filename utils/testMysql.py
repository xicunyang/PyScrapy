import pymysql

# 开启数据库
db = pymysql.connect("47.95.219.28", "root", "123456", "library", charset="utf8")

# 定义游标
cursor = db.cursor()
sql = "select * from t_user;"
cursor.execute(sql)
ips = cursor.fetchall()
print(ips)
db.commit()
# sql = "insert into t_ip(ip,create_time) values ('{0}',{1})".format()