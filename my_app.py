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
        return render_template("trains.html", data  = result)
    return redirect(url_for('login'))

@app.route("/reservation", methods = ['POST','GET'])
def reservation():
    if 'Select Your Berth' in session:
        return redirect(url_for('submit'))
    if request.method == 'POST':
        if request.form.get('Select Your Class'):
            session['Select Your Berth'] = request.form.get('Select Your Class', '')
            return redirect(url_for('submit'))
    return render_template("reservation.html")

@app.route("/setcookie", methods = ['POST', 'GET'])
def setcookie():
    print('request.method')
    if request.method == 'POST':
        berth = request.form['Select Your Berth']
        sclass = request.form['Select Your Class']
        obj = make_response(render_template('readcookie.html', berth = 'Select Your Berth', sclass = 'Select Your Class'))
        obj.set_cookie('Select Your Berth', berth)
        obj.set_cookie('Select Your Class', sclass )
        getcookie()
        return obj
    else:
        return redirect(url_for('reservation'))
    #return render_template("save.html")

@app.route("/getcookie", methods = ['GET'])
def getcookie():
    email = request.cookies.get('berth')
    print("======email is========", email)
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
    if 'Select Your Berth' in session:
        berth = session['Select Your Berth']
        return 'your berth is ' + berth + '<br>' + \
                "<b><a href = '/session/logout'> click here to log out</a></b>"
    return "your seat is confirmed"

@app.route('/session/login/', methods=['GET', 'POST'])
def session_login():
    if request.method == 'POST':
        cookies = request.cookies
        session['Select Your Berth'] = request.form['Select Your Berth']
        return redirect(url_for('reservation'))
    return '''
       <form action = "" method = "post">
          <p><input type = Select Your Berth = berth /></p>
          <p<<input type = submit value = Login /></p>
       </form>
       '''
@app.route('/session/logout')
def session_logout():
    # remove the username from the session if it is there
    session.pop('Select Your Berth', None)
    return redirect(url_for('reservation'))

if __name__ == "__main__":
    app.run(debug=True)