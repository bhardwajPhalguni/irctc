from flask import Flask, render_template, redirect, url_for, session, request, make_response
import psycopg2, json
import datetime
import decimal
from flask import Response
app = Flask(__name__)
app.secret_key = 'test12345'
hostname = 'aissot.openerp4you.com'
username = 'odoo'
password = 'odoo'
database = 'aissot_test'

class PostgresJsonEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            try:
                return (obj.strftime('%Y-%m-%d %HH:%MM:%SS'))
            except Exception as e:
                return str(e)
        if isinstance(obj, datetime.date):
            try:
                return (obj.strftime('%Y-%m-%d'))
            except Exception as e:
                return str(e)
        if isinstance(obj, decimal.Decimal):
            try:
                return float(obj)
            except Exception as e:
                return str(e)
#            return float(obj)
        return json.JSONEncoder.default(self, obj)

class PostgresConnector:
    def __init__(self):
        print("========dir===", dir(psycopg2))
        self.conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        self.conn.autocommit=True
        print("========self.conn===", dir(self.conn))
        self.cur = self.conn.cursor()

    #This function is used to check if db connection is established
    def ConnectToDatabase(self):
        try:
            self.conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
            self.conn.autocommit = True
            return "OK"
        except Exception as e:
            return str(e)

    def getTrainsDetails(self):
        try:
            if (not self.conn):
                self.ConnectToDatabase()
            cur = self.conn.cursor()
            query = "SELECT ID, Train_name, Starting_name, Destination_name_kms, Fare_Rs, Date_aug, Time_Arrival, Time_Department FROM trains"
            cur.execute(query)
            data = cur.fetchall()
            print("datadatadatadatadatadatadatadatadata", data)
            col = ('ID', 'train_name', 'starting_station', 'Destination_name_kms', 'Fare_Rs', 'Date_aug', 'Time_Arrival', 'Time_Departure')
            cur.close()
            results = []
            for val in data:
                temp = zip(col, val)
                print("=======temp=====a=", temp)
                temp = dict(temp)
                print("=======temp=====b=", temp)
                results.append(temp)
            #results = map(lambda x: dict(zip(col, x)), data)
            #res = json.dumps(results, cls=PostgresJsonEncoder)
            cur.close()
            #train = request.form.get('train', '')
            #obj = make_response(render_template("trains.html"))
            #train = obj.set_cookie('train',train)
            return results #Response(res, content_type='application/JSON; charset=utf-8')

        except Exception as e:
            cur.close()
            return str(e)

@app.route("/", methods =['POST', 'GET'])
def home():
    if 'username' in session:
        return redirect(url_for('about'))
    return redirect(url_for('login'))

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if 'username' in session:
        res = redirect(url_for('about'))
        email = request.form.get('email', '')
        print("========email===a============", email)
        res.set_cookie('email', email)
        return res

    if request.method == 'POST':
        print("========request.form========",request.form)
        if request.form.get('email'):
            session['username'] = request.form.get('email', '')
            res = redirect(url_for('about'))
            email = request.form.get('email', '')
            name = request.form.get('name', '')
            print("========email, name===b============", email, name)
            res.set_cookie('email', email)
            res.set_cookie('name', name)
            print("=====cookie-email======", request.cookies.get('email'))
            return res
    return render_template("index.html")

@app.route("/logout/", methods = ['POST', 'GET'])
def logout():
    if 'username' in session:
        session.pop('username')
    return redirect(url_for('home'))

@app.route("/form", methods = ['POST', 'GET'])
def about():
    res = make_response(render_template("form.html"))
    print("==========res=========", res)
    #res.set_cookie('temp', 1)
    print("==========res======b===", res)
    return res

@app.route("/trains", methods= ['POST','GET'])
def submit():
    if request.method == 'POST':
        db_obj = PostgresConnector()
        result = db_obj.getTrainsDetails()
        print("=======result========", result)
        print("===========request.form========", request.form)

        name = request.form.get('name', '')
        email = request.form.get('email', '')
        age = request.form.get('age', '')
        origin = request.form.get('origin', '')
        destination = request.form.get('destination', '')
        date = request.form.get('date', '')
        phone = request.form.get('phone', '')
        #Set Cookie
        res_obj = make_response(render_template("trains.html", data  = result))
        res_obj.set_cookie('name', name)
        res_obj.set_cookie('email', email)
        res_obj.set_cookie('age', age)
        res_obj.set_cookie('origin', origin)
        res_obj.set_cookie('destination', destination)
        res_obj.set_cookie('date', date)
        res_obj.set_cookie('phone', phone)
        return res_obj
    return redirect(url_for('login'))

@app.route("/reservation", methods = ['POST','GET'])
def reservation():
    print("==========request.method===========", request.method)
    #if request.method == 'POST':
    print("=======request.form========", request.form)
        #print("=======request.cookies_get========", request.cookies_get)

    if 'username' in session:
        berth = request.form.get('berth', '')
        bclass = request.form.get('bclass', '')
        obj = make_response(render_template("reservation.html"))
        obj.set_cookie('berth', berth)
        obj.set_cookie('bclass', bclass)
        return obj
    return redirect(url_for('submit'))
    #return redirect(url_for('save'))
        #print("======form.get======", obj)
        #return render_template("reservation.html")
    #return render_template("save.html")

@app.route("/save", methods=['POST', 'GET'])
def save():
    print("============request.method=================", request.method)
    if request.method == 'POST':
        print("========request.form========", request.form)
        dict = {}
        print("==========request.cookies==============", request.cookies)

        name = request.cookies.get('name', '')
        email = request.cookies.get('email', '')
        age = request.cookies.get('age', '')
        origin = request.cookies.get('origin', '')
        destination = request.cookies.get('destination', '')
        date = request.cookies.get('date', '')
        phone = request.cookies.get('phone', '')
        # Getting from form
        berth = request.form.get('berth', '')
        bclass = request.form.get('bclass', '')
        #train = request.form.get('train', '')
        dict = {}
        dict['name'] = name
        dict['email'] = email
        dict['age'] = age
        dict['origin'] = origin
        dict['destination'] = destination
        dict['berth'] = berth
        dict['bclass'] = bclass
        #dict['train'] = train
        dict['date'] = date
        dict['phone'] = phone
        print("======dict=======", dict)
        return render_template("save.html", data=[dict])
    return redirect(url_for('submit'))

@app.route("/setcookie", methods = ['POST', 'GET'])
def setcookie():
    print('request.method')
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        obj = make_response(render_template('readcookie.html', email = 'email', name = 'name'))
        obj.set_cookie('email', email)
        obj.set_cookie('name', name)
        getcookie()
        return obj

@app.route("/getcookie", methods = ['GET'])
def getcookie():
    email = request.cookies.get('berth')
    print("======email===============", email)
    conn = psycopg2.connect(host='aissot.openerp4you.com', user='odoo', password='odoo', dbname='aissot_test')
    print('--------conn----------', conn)
    cur = conn.cursor()
    print('--------cur--------', cur)
    query = "INSERT INTO cookie_cookie (ID, name, value) VALUES (1, 'email', email )"
    print("=======query======", query)
    cur.execute(query)
    conn.commit()
    cur.close() # 'email' is string, email is variable that value is coming from cookie
    return 'the email is ' + email

@app.route('/session/')
def home_session():
    cookies = request.cookies
    if 'name' in session:
        name = session['name']
        return 'your name is ' + name + '<br>' + \
                "<b><a href = '/session/logout'> click here to log out</a></b>"
    return "your seat is confirmed"

@app.route('/session/login/', methods=['GET', 'POST'])
def session_login():
    if request.method == 'POST':
        cookies = request.cookies
        session['name'] = request.form['name']
        return redirect(url_for('index'))
    return '''
       <form action = "" method = "post">
          <p><input type = name = name /></p>
          <p<<input type = submit value = Login /></p>
       </form>
       '''
@app.route('/session/logout')
def session_logout():
    # remove the username from the session if it is there
    session.pop('name', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)