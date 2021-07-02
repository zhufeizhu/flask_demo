# -*- coding: utf-8 -*-

from flask import Flask, request
import pymysql
import json

pymysql.install_as_MySQLdb()

app = Flask(__name__)

conn = pymysql.Connect(
    host='127.0.0.1',
    port= 3306,
    user='user',
    passwd='root',
    db='info',
    charset='utf8')

cursor = conn.cursor()

@app.route('/',methods={'POST'})
def hello_world():
    sql = 'select * from student;'
    cursor.execute(sql)
    results = cursor.fetchall()
    res = []
    student={}
    for row in results:
        student['id'] = row[0]
        student['name'] = row[1]
        student["sex"] = row[2]
        res.append(student)
    
    return json.dumps(res,ensure_ascii=False)

if __name__ == "__main__":
    app.run(host="127.0.0.1",port=5000)