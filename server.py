# -*- coding: iso_8859_1 -*-

from flask import Flask, request, send_file
from flask.helpers import make_response
import pymysql
import json
import io
import os
import threading

from werkzeug.wrappers import response

pymysql.install_as_MySQLdb()

app = Flask(__name__)

conn = pymysql.Connect(
    host='127.0.0.1',
    port= 3306,
    user='exam',
    passwd='P@ssw0rd',
    db='exam_db',
    charset='utf8') 

cursor = conn.cursor()

lock = threading.RLock()

basepath = os.path.abspath(os.path.dirname(__file__))

#管理员审核 审核 1表示未审核 2表示审核未通过 3表示审核通过
@app.route('/adminRent',methods={'POST'})
def adminRent():
    sql = "select rentInfo.Id as rentId,Name,Startday,Finishday,Starttime,"\
          "Finishtime,Brand,Color,Platenumber,Image1,rentInfo.Userid,Cartabstate from rentInfo inner join carInfo "\
          "on rentInfo.Carid = carInfo.Id inner join userInfo on rentInfo.Userid = userInfo.Id "\
          "where Cartabstate = 1 or Cartabstate = 2 or Cartabstate = 3"
    lock.acquire()
    num = cursor.execute(sql)
    lock.release()
    if num == 0:
        return ""
    res = cursor.fetchall()
    rents = []
    for row in res:
        rent = {}
        rent['rentId'] = row[0]
        rent['name'] = row[1]
        rent['startDay'] = row[2]
        rent['finishDay'] = row[3]
        rent['startTime'] = row[4]
        rent['finishTime'] = row[5]
        rent['brand'] = row[6]
        rent['color'] = row[7]
        rent['platenumber'] = row[8]
        rent['icon'] = row[9].decode('iso_8859_1')
        rent['userId'] = row[10]
        rent['cartabState'] = row[11]
        rents.append(rent)
    return json.dumps(rents,ensure_ascii=False)

# #管理员审核 审核 2表示未审核通过 3表示审核通过
# @app.route('/adminRentResult',methods={'POST'})
# def adminRentResult():
#     sql = "select rentInfo.Id as rentId,Name,Startday,Starttime,Finishday,"\
#           "Finishtime,Brand,Color,Platenumber,Image1,Cartabstate from rentInfo inner join carInfo "\
#           "on rentInfo.Carid = carInfo.Id where Cartabstate = 2 or Cartabstate = 3"
#     print(cursor.execute(sql))
#     res = cursor.fetchall()
#     rents = []
#     rent = {}
#     for row in res:
#         rent['rentId'] = row[0]
#         rent['name'] = row[1]
#         rent['startDay'] = row[2]
#         rent['finishDay'] = row[3]
#         rent['startTime'] = row[4]
#         rent['finishTime'] = row[5]
#         rent['brand'] = row[6]
#         rent['color'] = row[7]
#         rent['platenumber'] = row[8]
#         rent['icon'] = row[9].decode('iso_8859_1')
#         rent['cartabState'] = row[10]
#         rents.append(rent)
#     return json.dumps(rents)

#审核结果
@app.route('/adminRentUpdate',methods={'POST'})
def adminRentUpdate():
    state = request.form['state']
    id = request.form['rentId']
    sql = "update rentInfo set Cartabstate = %s where Id = %s"
    lock.acquire()
    cursor.execute(sql,(state,id))
    lock.release()
    conn.commit()
    return 'OK'

#添加新的车辆
@app.route('/newCar',methods={'POST'})
def newCar():
    #车牌
    platenumber = request.form['platenumber']
    #型号
    brand = request.form['brand']
    #颜色
    color = request.form['color']
    #车主ID
    userid = request.form['userId']
    #
    carinfostate = request.form['carinfostate']
    remarks = request.form['remarks']
    image1 = request.form['image1'].encode('iso_8859_1')
    image2 = request.form['image2'].encode('iso_8859_1')
    image3 = request.form['image3'].encode('iso_8859_1')
    image4 = request.form['image4'].encode('iso_8859_1')

    sql = "insert into exam_db.carInfo(Platenumber,Brand,Color,Userid,Carinfostate,Remarks,Image1,Image2,Image3,Image4)"\
          "values"\
          "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" 
    lock.acquire()
    cursor.execute(sql,(platenumber,brand,color,userid,carinfostate,remarks,pymysql.Binary(image1),pymysql.Binary(image2),pymysql.Binary(image3),pymysql.Binary(image4)))
    lock.release()
    print(conn.commit())
    return 'OK'

@app.route('/showCarDetail',methods={'POST'})
def showCarDetail():
    carid = request.form['carId']
    sql = "select Platenumber,Brand,Color,Image1,Image2,Image3,Image4 from carInfo where Id = %s"
    lock.acquire()
    num = cursor.execute(sql,(carid))
    lock.release()
    if num == 0:
        return ""
    res = cursor.fetchall()
    row = res[0]
    car = {}
    car['platenumber'] = row[0]
    car['brand'] = row[1]
    car['color'] = row[2]
    car['image1'] = row[3].decode('iso_8859_1')
    car['image2'] = row[4].decode('iso_8859_1')
    car['image3'] = row[5].decode('iso_8859_1')
    car['image4'] = row[6].decode('iso_8859_1')
    return json.dumps(car)

@app.route('/deleteCar',methods={'POST'})
def deleteCar():
    carid = request.form['carId']
    sql = "delete from carInfo where Id = %s"
    lock.acquire()
    cursor.execute(sql,(carid))
    lock.release()
    conn.commit()
    return 'OK'

# 我的车辆
@app.route('/showMyCar',methods={'POST'})
def showMyCar():
    userid = request.form['userId']
    sql = "select * from exam_db.carInfo where Userid = '" + str(userid) + "'"
    lock.acquire()
    num = cursor.execute(sql)
    lock.release()
    if num == 0:
        return ""

    res = cursor.fetchall()
    cars = []
    for row in res:
        car = {}
        car['carId'] = row[0]
        car['platenumber'] = row[1]
        car['brand'] = row[2]
        car['color'] = row[3]
        car['icon'] = row[7].decode('iso_8859_1')
        cars.append(car)
    return json.dumps(cars,ensure_ascii=False)

#添加新的租车信息
@app.route('/newRent',methods={'POST'})
def newRent():
    userid = request.form['userid']
    carid = request.form['carid']
    startday = request.form['startday']
    finishday = request.form['finishday']
    starttime = request.form['starttime']
    finishtime = request.form['finishtime']
    cartabstate = "1"

    sql = "insert into exam_db.rentInfo(Userid,Carid,Startday,Finishday,Starttime,Finishtime,Cartabstate)"\
          "values"\
          "(" + str(userid) + "," + str(carid) + ",'" + str(startday) + "','" + str(finishday) + "','" + str(starttime)\
          + "','" + str(finishtime) + "'," + str(cartabstate) +")"
    lock.acquire()
    cursor.execute(sql)
    lock.release()
    conn.commit()
    return 'OK'

# 已发布 1表示未审核 2表示审核未通过 3 表示审核通过
@app.route('/showMyRent',methods={'POST'})
def showMyRent():
    userid = request.form['userId']
    sql = "select rentInfo.Id as rentId,rentInfo.Userid as userId,Startday,Starttime,Finishday,Finishtime,"\
          "Brand,Color,Platenumber,Image1,Cartabstate from rentInfo inner join carInfo on rentInfo.Carid = carInfo.Id "\
          "where (Cartabstate = %s or Cartabstate = %s or Cartabstate = %s) and rentInfo.Userid = %s"
    lock.acquire()
    num = cursor.execute(sql,("1","2","3",userid))
    lock.release()
    if num == 0:
        return ""
    res = cursor.fetchall()
    rents = []
    for row in res:
        rent = {}
        rent['rentId'] = row[0]
        rent['userId'] = row[1]
        rent['startDay'] = row[2]
        rent['startTime'] = row[3]
        rent['finishDay'] = row[4]
        rent['finishTime'] = row[5]
        rent['brand'] = row[6]
        rent['color'] = row[7]
        rent['platenumber'] = row[8]
        rent['icon'] = row[9].decode('iso_8859_1')
        rent['cartabState'] = row[10]
        rents.append(rent)
    return json.dumps(rents,ensure_ascii=False)

#收车 6表示车已经被回收 租车结束
@app.route('/recycleRent',methods={'POST'})
def recycleRent():
    rentid = request.form['rentId']
    sql = 'update rentInfo set Cartabstate = 6 where Id = %s'
    lock.acquire()
    cursor.execute(sql,(rentid))
    lock.release()
    conn.commit()
    return 'OK'

# 新订单 4表示正在被租 5表示待收车 6表示租车结束
@app.route('/showNewRent',methods={'POST'})
def showNewRent():
    userid = request.form['userId']
    sql = "select carInfo.Userid as userid,orderInfo.Id as orderid,Appointday,Appointtime,rentInfo.Id as rentid,"\
          "Startday,Starttime,Finishday,Finishtime,Telephone,Brand,Color,Platenumber,Image1,Cartabstate "\
          "from orderInfo inner join rentInfo on orderInfo.Cartabid = rentInfo.Id inner join carInfo "\
          "on carInfo.Id = rentInfo.Carid where carInfo.Userid = %s and (Cartabstate = 4 or Cartabstate = 5 or Cartabstate = 6)"
    lock.acquire()
    num = cursor.execute(sql,(userid))
    lock.release()
    if num == 0:
        return ""
    res = cursor.fetchall()
    rents = []
    for row in res:
        rent = {}
        rent['userId'] = row[0]
        rent['orderId'] = row[1]
        rent['appointDay'] = row[2]
        rent['appointTime'] = row[3]
        rent['rentId'] = row[4]
        rent['startDay'] = row[5]
        rent['startTime'] = row[6]
        rent['finishDay'] = row[7]
        rent['finishTime'] = row[8]
        rent['telephone'] = row[9]
        rent['brand'] = row[10]
        rent['color'] = row[11]
        rent['platenumber'] = row[12]
        rent['icon'] = row[13].decode('iso_8859_1')
        rent['cartabState'] = row[14]
        rents.append(rent)
    return json.dumps(rents,ensure_ascii=False)

# 主页 3表示审核通过的
@app.route('/showRent',methods={'POST'})
def showRent():
    sql = "select rentInfo.Id as id,Startday,Finishday,Starttime,Finishtime,Platenumber,Brand,Color,Image1,Name "\
          "from exam_db.rentInfo inner join exam_db.carInfo on exam_db.rentInfo.CarId = exam_db.carInfo.Id "\
          "inner join userInfo on userInfo.Id = rentInfo.Userid where exam_db.rentInfo.Cartabstate = 3"
    lock.acquire()
    num = cursor.execute(sql)
    lock.release()
    if num == 0:
        return ""
    res = cursor.fetchall()
    rents = []
    for row in res:
        rent = {}
        rent['id'] = row[0]
        rent['startDay'] = row[1]
        rent['finishDay'] = row[2]
        rent['startTime'] = row[3]
        rent['finishTime'] = row[4]
        rent['platenumber'] = row[5]
        rent['brand'] = row[6]
        rent['color'] = row[7]
        rent['icon'] = row[8].decode('iso_8859_1')
        rent['name'] = row[9]
        rents.append(rent)
    return json.dumps(rents,ensure_ascii=False)

#主页预约 4表示正在被约
@app.route('/newOrder',methods={'POST'})
def newOrder():
    cartabid = request.form['cartabid']
    appointday = request.form['appointday']
    appointtime = request.form['appointtime']
    employerid = request.form['employerid']
    telephone = request.form['telephone']
    orderstate = request.form['orderstate']
    sql = "insert into exam_db.orderInfo(Cartabid,Appointday,Appointtime,Employerid,Telephone,Orderstate)"\
          "values"\
          "(%s,%s,%s,%s,%s,%s)"
    lock.acquire()
    cursor.execute(sql,(cartabid,appointday,appointtime,employerid,telephone,orderstate))
    lock.release()
    conn.commit()
    sql = "update rentInfo set Cartabstate = 4 where Id = %s"
    cursor.execute(sql,(cartabid))
    return 'OK'

#预约 取消预约 1表示订单已经结束
@app.route('/cancelOrder',methods={'POST'})
def cancelOrder():
    orderid = request.form['orderId']
    rentid = request.form['rentId']
    sql = "update orderInfo set Orderstate = 1 where Id = %s"
    lock.acquire()
    cursor.execute(sql,(orderid))
    lock.release()
    conn.commit()
    sql = "update rentInfo set Cartabstate = 5 where Id = %s"
    lock.acquire()
    cursor.execute(sql,(rentid))
    lock.release()
    conn.commit()
    return 'OK'


#我的预约 全部 0表示正在进行 1表示已经结束
@app.route('/showMyOrder',methods={'POST'})
def showMyOrder():
    employerid = request.form['employerid']
    sql = "select orderInfo.Id as orderid,Appointday,Appointtime,rentInfo.Id as rentid,Startday,"\
          "Finishday,Starttime,Finishtime,Telephone,Platenumber,Brand,Color,Orderstate,Image1,Name "\
          "from orderInfo inner join rentInfo on orderInfo.Cartabid = rentInfo.Id inner join carInfo "\
          "on carInfo.Id = rentInfo.Carid inner join userInfo on rentInfo.Userid = userInfo.Id where Employerid = %s"
    lock.acquire()
    num = cursor.execute(sql,(employerid))
    lock.release()
    if num == 0:
        return ""
    res = cursor.fetchall()
    orders = []
    for row in res:
        order = {}
        order['orderId'] = row[0]
        order['appointDay'] = row[1]
        order['appointTime'] = row[2]
        order['rentId'] = row[3]    
        order['startDay'] = row[4]
        order['finishDay'] = row[5]
        order['startTime'] = row[6]
        order['finishTime'] = row[7]
        order['telephone'] = row[8]
        order['platenumber'] = row[9]
        order['brand'] = row[10]
        order['color'] = row[11]
        order['orderState'] = row[12]
        order['icon'] = row[13].decode('iso_8859_1')
        order['name'] = row[14]
        orders.append(order)
    return json.dumps(orders,ensure_ascii=False)

#我的预约 预约中
@app.route('/showInOrder',methods={'POST'})
def showInOrder():
    employerid = request.form['employerid']
    sql = "select orderInfo.Id as orderid,Appointday,Appointtime,rentInfo.Id as rentid,Startday,"\
          "Finishday,Starttime,Finishtime,Telephone,Platenumber,Brand,Color,Image1,Name "\
          "from orderInfo inner join rentInfo on orderInfo.Cartabid = rentInfo.Id inner join carInfo "\
          "on carInfo.Id = rentInfo.Carid inner join userInfo on rentInfo.Userid = userInfo.Id where Employerid = %s"\
          " and Orderstate = 0"    
    lock.acquire()
    num = cursor.execute(sql,(employerid))
    lock.release()
    if num == 0:
        return ""
    res = cursor.fetchall()
    orders = []
    for row in res:
        order = {}
        order['orderId'] = row[0]
        order['appointDay'] = row[1]
        order['appointTime'] = row[2]
        order['rentId'] = row[3]    
        order['startDay'] = row[4]
        order['finishDay'] = row[5]
        order['startTime'] = row[6]
        order['finishTime'] = row[7]
        order['telephone'] = row[8]
        order['platenumber'] = row[9]
        order['brand'] = row[10]
        order['color'] = row[11]
        order['icon'] = row[12].decode('iso_8859_1')
        order['name'] = row[13]
        orders.append(order)
    return json.dumps(orders,ensure_ascii=False)

#我的预约 已结束
@app.route('/showOverOrder',methods={'POST'})
def showOverOrder():
    employerid = request.form['employerid']
    sql = "select orderInfo.Id as orderid,Appointday,Appointtime,rentInfo.Id as rentid,Startday,"\
          "Finishday,Starttime,Finishtime,Telephone,Platenumber,Brand,Color,Image1,Name "\
          "from orderInfo inner join rentInfo on orderInfo.Cartabid = rentInfo.Id inner join carInfo "\
          "on carInfo.Id = rentInfo.Carid inner join userInfo on rentInfo.Userid = userInfo.Id where Employerid = %s"\
          " and Orderstate = 1"    
    lock.acquire()
    num = cursor.execute(sql,(employerid))
    lock.release()
    if num == 0:
        return ""
    res = cursor.fetchall()
    orders = []
    for row in res:
        order = {}
        order['orderId'] = row[0]
        order['appointDay'] = row[1]
        order['appointTime'] = row[2]
        order['rentId'] = row[3]    
        order['startDay'] = row[4]
        order['finishDay'] = row[5]
        order['startTime'] = row[6]
        order['finishTime'] = row[7]
        order['telephone'] = row[8]
        order['platenumber'] = row[9]
        order['brand'] = row[10]
        order['color'] = row[11]
        order['icon'] = row[12].decode('iso_8859_1')
        order['name'] = row[13]
        orders.append(order)
    return json.dumps(orders,ensure_ascii=False)

#登录
@app.route('/login',methods={'POST'})
def login():
    account = request.form['account']
    password = request.form['password']
    sql = "select Id,Name,Image,Isadmin,Username,Sex from exam_db.userInfo "\
          "where Account = %s and Password = %s"
    lock.acquire()
    num = cursor.execute(sql,(account,password))
    lock.release()
    if num == 0:
        return ""
    results = cursor.fetchall()
    res = {}
    if len(results) > 0:
        row = results[0]
        res['Id'] = row[0]
        res['name'] = row[1]
        res['image'] = row[2].decode('iso_8859_1')
        res['type'] = 'True'
        res['Isadmin'] = row[3]
        res['userName'] = row[4]
        res['sex'] = row[5]
    else:
        res['type'] = 'False'
    return json.dumps(res,ensure_ascii=False)

@app.route('/hello',methods={'GET','POST'})
def hello():
    data = request.form['data']
    return data


@app.route('/register',methods={'POST'})
def regiser():
    account = request.form['account']
    username = request.form['username']
    password = request.form['password']
    name = request.form['name']
    sex = request.form['sex']
    number = request.form['number']
    isadmin = 0
    image = request.form["image"].encode('iso_8859_1')
    sql = "insert into exam_db.userInfo (Account,Username,Password,Name,Sex,Number,Isadmin,Image)"\
          "values"\
          "('" + str(account) + "','" + str(username) + "','" + str(password) + "','" + str(name) + "','" + str(sex) + "','" + str(number) + "',0,%s)"
    lock.acquire()
    cursor.execute(sql,(pymysql.Binary(image)))
    lock.release()
    ret = conn.commit()
    return 'OK'

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000)