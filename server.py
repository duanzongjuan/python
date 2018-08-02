from flask import Flask,render_template,session,redirect,url_for,request
#识别字体
import chardet,pymysql,analysisEmail,send

#创建app(每一个server文件都有一个__name__)
app = Flask(__name__)
#密钥
app.secret_key = "123"

#route路由(装饰器),服务器中有这个路由,才能访问
@app.route("/") #app的首页
def index():
    #if session["username"] != None:
    if session.get("username") != None:
        return render_template("index.html")
    else:
        return redirect(url_for("login")) #redirect用于跳转  url_for用于将字符串转换为url地址,用于跳转到该页面

@app.route("/login")
def login():
    if session.get("username") != None:
        return redirect(url_for("index"))
    else:
        return render_template("login.html")

@app.route("/changePassword")
def changePassword():
    if session.get("username") != None:
        return render_template("changePassword.html")
    else:
        return redirect(url_for("login"))

@app.route("/getEmail")
def getEmail():
    if session.get("username") != None:
        return render_template("getEmail.html")
    else:
        return redirect(url_for("login"))

@app.route("/regin")
def regin():
    if session.get("username") != None:
        return redirect(url_for("index"))
    else:
        return render_template("regin.html")

@app.route("/sendEmail")
def sendEmail():
    if session.get("username") != None:
        return render_template("sendEmail.html")
    else:
        return redirect(url_for("login"))

@app.route("/show")
def show():
    if session.get("username") != None:
        return render_template("show.html")
    else:
        return redirect(url_for("login"))

@app.route("/checkLogin",methods = ['POST'])
def checkLogin():
    username = request.form["username"]
    password = request.form["password"]
    if username != None and password != None:
        #查询数据库
        #连接数据库
        db = pymysql.connect("localhost","root","root","email")
        #创建游标
        cursor = db.cursor()
        #组织sql语句
        sql = "select * from users where username = '%s' "%username
        #执行sql语句
        cursor.execute(sql)
        #查询数据
        res = cursor.fetchall()
        if len(res) > 0:
            if res[0][2] == password:
                session['username'] = username
                return "ok"
            else:
                return "no"
        else:
            return "no"
#退出登录
@app.route("/loginout")
def loginout():
    if session.get("username") != None:
        #清除session
        session.pop("username")
    return redirect(url_for("login"))

#注册
@app.route("/addUser",methods = ['POST'])
def addUser():
    username = request.form['username']
    password = request.form['password']
    #操作数据库
    db = pymysql.connect("localhost","root","root","email")
    #游标,用于指向数据的第几行
    cursor = db.cursor()
    #先检查用户表中是否有该用户
    sql ="select * from users where username='%s'"%username
    cursor.execute(sql)
    res = cursor.fetchall()
    if len(res) > 0:
        return "has"
    else:
        #插入数据
        sql = "insert into users(username,password) values('%s','%s')"%(username,password)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            return "no"
        return 'ok'

#发送邮件
@app.route("/put",methods=['POST'])
def put():
    f = request.files['file']
    email = request.form['email']
    print(email)
    if f:
        con = f.read()
        charobj = chardet.detect(con)
        con = con.decode(charobj['encoding'])
        #过滤邮件头部
        index = con.index("\n\n")
        con = con[index::]
        #判断邮件内容con
        judgeobj = analysisEmail.judgeEmail()
        info,P,email_order_ratio = judgeobj.judge(con)
        if P>0.9:
            string = "《这是垃圾邮件,建议删除》" + con
        else:
            string = "《这是正常邮件》" + con
        sendObj = send.Send()
        sendObj.sendEmail(string,email)
    return render_template("show.html",data=(info,P,email_order_ratio))

#
@app.route("/editPassword",methods=['POST'])
def editPassword():
    password = request.form['password']
    old = request.form['old']
    #操作数据库
    db = pymysql.connect("localhost","root","root","email")
    cursor = db.cursor()
    username = session.get('username')
    sql = "select * from users where username='%s'"%username
    cursor.execute(sql)
    res = cursor.fetchall()
    if len(res) > 0 and res[0][2] == old:
        sql = "update users set password='%s' where username ='%s' "%(password,username)
        cursor.execute(sql)
        db.commit()
        #清空用户名
        session.pop('username')
        return "ok"
    else:
        return "no"

if __name__ == "__main__":
    app.run(debug=True)
