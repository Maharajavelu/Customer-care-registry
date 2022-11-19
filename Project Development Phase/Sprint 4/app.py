from flask import Flask, render_template, request, redirect, url_for, session
import ibm_db
import re
from flask_mail import Mail, Message

app = Flask(__name__)
mail = Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'customercare.in2022@gmail.com'
app.config['MAIL_PASSWORD'] = 'dutxqvejaxonmmew'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


app.secret_key='a'
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=54a2f15b-5c0f-46df-8954-7e38e612c2bd.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32733;Security=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=fqt70379;PWD=KdUUJ3RnMlMqAimg;",'','')

@app.route('/')
def home():
    return render_template('/home.html')

@app.route('/registertemp',methods=["POST","GET"])
def registertemp():
    return render_template("register.html")

@app.route('/uploaddata',methods =['GET','POST'])
def register():
    msg = ''
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']  
        stmt = ibm_db.prepare(conn, 'SELECT * FROM users WHERE username = ?')
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt) 
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'^[A-Za-z0-9_.-]*$', username):
            msg = 'name must contain only characters and numbers !'
        else:
            prep_stmt = ibm_db.prepare(conn,'INSERT INTO users(firstname, lastname, username, email, password, address) VALUES(?, ?, ?, ?, ?, ?)')
            ibm_db.bind_param(prep_stmt, 1, firstname)
            ibm_db.bind_param(prep_stmt, 2, lastname)
            ibm_db.bind_param(prep_stmt, 3, username)
            ibm_db.bind_param(prep_stmt, 4, email)
            ibm_db.bind_param(prep_stmt, 5, password)
            ibm_db.bind_param(prep_stmt, 6, address)
            ibm_db.execute(prep_stmt)
            msg = 'Dear % s You have successfully registered!'%(username)
            msg1 = Message('Hello', sender = 'customercare.in2022@gmail.com', recipients = [email])
            msg1.body = 'Hello'+ username +''', 
                        Account creation in customer care registry was successful.
                        For raising Complaints, login with your username and password.
                        Thank You)'''
            mail.send(msg1)
        return render_template('register.html',a = msg,indicator="success")
    else:
        msg = 'Please fill the form!'
    return render_template('register.html',a = msg, indicator='failure')

@app.route('/login',methods=["POST","GET"])
def login():
    return render_template("login.html")

@app.route('/logindata',methods=["POST","GET"])
def logindata():
    global userid
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        stmt = ibm_db.prepare(conn,'SELECT * FROM users WHERE username = ? AND password = ?')
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_tuple(stmt)
        if account:
            session['id'] = account[0]
            userid =  account[0]
            session['username'] = account[1]
            return redirect(url_for('dashboard'))
        else:
            msg = 'Incorrect username / password !'
            return render_template('login.html', b = msg, indicator="failure")

@app.route('/home')
def dashboard():
    if 'id' in session:
        uid = session['id']
        stmt = ibm_db.prepare(conn, 'SELECT * FROM users WHERE id = ?')
        ibm_db.bind_param(stmt, 1, uid)
        ibm_db.execute(stmt)
        ibm_db.fetch_tuple(stmt)
        username = session['username']
        return render_template('user dashboard.html', name = username)
    return render_template('user dashboard.html')

@app.route('/profile',methods=["POST","GET"])
def profile():
    if 'id' in session:
        uid = session['id']
        stmt = ibm_db.prepare(conn, 'SELECT * FROM users WHERE id = ?')
        ibm_db.bind_param(stmt, 1, uid)    
        ibm_db.execute(stmt)
        acc = ibm_db.fetch_tuple(stmt)        
        return render_template('userprofile.html',fullname=acc[1]+acc[2],username=acc[3],email=acc[4],address=acc[6])
    return render_template('userprofile.html')

@app.route('/edit')
def edit():
    return render_template('editprofile.html')

@app.route('/editprofile', methods=["POST","GET"])
def editprofile():
    if request.method == 'POST' :
        msg = ''
        if 'id' in session:
            uid = session['id']
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            username = request.form['username']
            email = request.form['email']
            address = request.form['address'] 
            stmt = ibm_db.prepare(conn,"UPDATE users SET firstname = ?, lastname = ?, username = ?, email = ?, address = ? WHERE id = ?")
            ibm_db.bind_param(stmt, 1, firstname)
            ibm_db.bind_param(stmt, 2, lastname)
            ibm_db.bind_param(stmt, 3, username)
            ibm_db.bind_param(stmt, 4, email)
            ibm_db.bind_param(stmt, 5, address)
            ibm_db.bind_param(stmt, 6, uid)
            ibm_db.execute(stmt)
            msg = 'Profile Updated Successfully!'
            return render_template('editprofile.html',a = msg)
    return render_template('editprofile.html')


@app.route('/addcomplaint',methods=["POST","GET"])
def addcomplaint():
    if request.method == "POST":
        if 'id' in session:
            msg = ''
            uid=session['id']
            selectcategory = request.form['selectcategory']
            date = request.form['dt']
            phone = request.form['phone']
            state = request.form['state']
            email = request.form['email']
            complaint = request.form.get('complaint')
            stmt = ibm_db.prepare(conn,"SELECT * FROM users WHERE id = ?")
            ibm_db.bind_param(stmt, 1, uid)
            ibm_db.execute(stmt)
            acc = ibm_db.fetch_tuple(stmt)
            email = acc[4]
            prep_stmt = ibm_db.prepare(conn,'INSERT INTO complaintdetails(uid, selectcategory, dt , phone, state, email, complaint, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)')
            ibm_db.bind_param(prep_stmt, 1, uid)
            ibm_db.bind_param(prep_stmt, 2, selectcategory)
            ibm_db.bind_param(prep_stmt, 3, date)
            ibm_db.bind_param(prep_stmt, 4, phone)
            ibm_db.bind_param(prep_stmt, 5, state)
            ibm_db.bind_param(prep_stmt, 6, email)
            ibm_db.bind_param(prep_stmt, 7, complaint)
            ibm_db.bind_param(prep_stmt, 8, 'pending')
            ibm_db.execute(prep_stmt)
            msg = 'You have successfully registered your complaint'
            TEXT1 = Message('Hello', sender = 'customercare.in2022@gmail.com', recipients = [email])
            TEXT1.body =  """ Dear """+acc[1]+" "+acc[2]+"""
                        Your complaint has been succesfully registered...!!
                        One of our agent is assigned , will surely resolve your complaint as soon as possible
                        Please check the complaint details in dashboard for status of complaint."""
            mail.send(TEXT1)
            se = ibm_db.exec_immediate(conn, 'SELECT * FROM agentinfo ORDER BY RAND() LIMIT 1')
            agmail = ibm_db.fetch_tuple(se)
            agentemail = agmail[1]
            TEXT = Message('Hello', sender = 'customercare.in2022@gmail.com', recipients = [agentemail])
            TEXT.body = """New Complaint from """+acc[1]+" "+acc[2]+""" 
                    Complaint Description :
                    """+complaint+""""""
            mail.send(TEXT)
            return render_template('userlodgecomp.html',a = msg)
    return render_template('userlodgecomp.html')


@app.route('/view',methods=["POST","GET"])
def view():
    if 'id' in session:
        return render_template('usercomphist.html')

@app.route('/comphistory',methods=['POST','GET'])
def compview(): 
    if 'id' in session:
        uid=session['id']
        stmt = ibm_db.prepare(conn, 'SELECT * FROM users WHERE id = ? ')
        ibm_db.bind_param(stmt, 1, uid)    
        ibm_db.execute(stmt)
        
        stmt1 = ibm_db.prepare(conn, 'SELECT id, selectcategory, dt, phone, state, email, complaint, status FROM complaintdetails WHERE uid = ?')
        ibm_db.bind_param(stmt1, 1, uid)
        ibm_db.execute(stmt1)
        comp = ibm_db.fetch_assoc(stmt1)
        data = []
        while comp != False:
            data.append(comp)
            comp = ibm_db.fetch_assoc(stmt1)
        return render_template('usercomphist.html', complaints = data)
    return render_template('usercomphist.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/adminpage')
def adminpage():
    return render_template('admin dashboard.html')

@app.route('/adminlog',methods=["POST","GET"])
def adminlog():
    msg = ''
    email = request.form['email']
    password = request.form['password']
    stmt = ibm_db.prepare(conn, 'SELECT * FROM admininfo  WHERE email = ?  and password = ?')
    ibm_db.bind_param(stmt,1, email)
    ibm_db.bind_param(stmt,2, password)
    ibm_db.execute(stmt)
    logged = ibm_db.fetch_assoc(stmt)
    if(logged):
        msg = 'successfully loggedin'
        return render_template("admin dashboard.html",a=msg)
    else:
        return render_template("admin.html",a="Incorrect email/password")

@app.route('/adcomplainthist',methods=['POST','GET'])
def adcomplainthist(): 
        stmt1 = ibm_db.prepare(conn, 'SELECT * FROM complaintdetails')
        ibm_db.execute(stmt1)
        comp = ibm_db.fetch_assoc(stmt1)
        data = []
        while comp != False:
            data.append(comp)
            comp = ibm_db.fetch_assoc(stmt1)
        return render_template('admincomphist.html', complaints = data)

@app.route('/agcomplainthist',methods=['POST','GET'])
def agcomplainthist(): 
        stmt1 = ibm_db.prepare(conn, 'SELECT * FROM complaintdetails')
        ibm_db.execute(stmt1)
        comp = ibm_db.fetch_assoc(stmt1)
        data = []
        while comp != False:
            data.append(comp)
            comp = ibm_db.fetch_assoc(stmt1)
        return render_template('admincomphist.html', complaints = data)

@app.route('/agentcreate',methods=["POST","GET"])
def agentcreate():
    return render_template('adminagent.html')

@app.route('/agentdata',methods=["POST","GET"])
def agentdata():
    msg = ''
    username = request.form['username']
    password = request.form['password']
    stmt = ibm_db.prepare(conn,'INSERT INTO agentinfo(username, password) VALUES (?, ?)')
    ibm_db.bind_param(stmt, 1, username)
    ibm_db.bind_param(stmt, 2, password)
    ibm_db.execute(stmt)
    msg = 'Agent has been created successfully'
    return render_template('adminagent.html',a = msg)

@app.route('/agent',methods=["POST","GET"])
def agent():
    return render_template('agent.html')

@app.route('/agentlogin',methods=["POST","GET"])
def agentlogin():
    msg = ''
    email = request.form['username']
    password = request.form['password']
    stmt = ibm_db.prepare(conn, 'SELECT * FROM agentinfo  WHERE username = ?  and password = ?')
    ibm_db.bind_param(stmt,1, email)
    ibm_db.bind_param(stmt,2, password)
    ibm_db.execute(stmt)
    logged = ibm_db.fetch_assoc(stmt)
    if(logged):
        msg = 'successfully loggedin'
        return render_template("agentdashboard.html",a=msg)
    else:
        return render_template("agent.html",a="Incorrect email/password")

@app.route('/agentpage')
def agentpage():
    return render_template('agentdashboard.html')

@app.route('/loggout')
def loggout():
    if 'id ' in session:
        session.pop('id',None)
        session.pop('email',None)
        session.pop('password',None)
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/solved/<no>')
def solved(no):
    i = no
    stmt = ibm_db.prepare(conn, "UPDATE complaintdetails SET status = ? WHERE id = ?")
    ibm_db.bind_param(stmt, 1, 'solved')
    ibm_db.bind_param(stmt, 2, i)
    ibm_db.execute(stmt)
    se = ibm_db.prepare(conn, 'SELECT * FROM complaintdetails where id = ?')
    ibm_db.bind_param(se, 1, i)
    ibm_db.execute(se)
    em = ibm_db.fetch_tuple(se)
    email = em[6]
    print(email)
    TEXT = Message('Hello', sender = 'customercare.in2022@gmail.com', recipients = [email])
    TEXT.body = """Your Complaint has been solved."""
    mail.send(TEXT)
    return render_template('solve.html', a ="Complaint Resolved" )


if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0',port=8080)