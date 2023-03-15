from flask import Flask, render_template, request, redirect, jsonify
# from flask.ext.jsonpify import jsonify
from flask_mysqldb import MySQL
import yaml
from enum import Enum
 
class Occupation(Enum):
    STUDENT = 1
    CDS_EMPLOYEE = 2
    COMPANY_POC = 3

USER = Occupation.STUDENT

app = Flask(__name__)

# Configure db
db = yaml.safe_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Fetch form data
        userDetails = request.form
        name = userDetails['name']
        email = userDetails['email']
        cur = mysql.connection.cursor()
        # cur.execute("INSERT INTO users(name, email) VALUES(%s, %s)",(name, email))
        mysql.connection.commit()
        cur.close()
        return redirect('/tables')
    return render_template('index.html')

@app.route('/opportunities')
def get_opportunities():

    student_id = request.args.get('student_id')
    student_id = int(student_id)
    status = request.args.get('status')

    if(USER != Occupation.STUDENT):
        return jsonify({"error": "Invalid Access"}), 404
    
    if student_id is None and status is None:
        cur = mysql.connection.cursor()
        resultValue = cur.execute("select * from opportunity")
        if resultValue > 0:
            opportunities = cur.fetchall()
            return jsonify(opportunities)
    else:
        cur = mysql.connection.cursor()
        if status == 'applied':
            query = "select * from selection_procedure where opp_id in (select opp_id from app_opp where student_id = %s)"
            resultValue = cur.execute(query, (student_id,))
            if resultValue>0:
                opportunities = cur.fetchall()
                return jsonify(opportunities)
        elif status == 'rejected' or status == 'eligible' or status == 'not_eligible' or status == 'accepted':
            query = "select * from opportunity where opp_id in (select opp_id from app_opp where student_id = %s)"
            resultValue = cur.execute(query, (student_id,))
            if resultValue>0:
                opportunities = cur.fetchall()
                return jsonify(opportunities)
        else:
            return jsonify({"error": "invalid status"}), 404

@app.route('/opportunity')
def get_opportunity_by_id():
    if(USER != Occupation.STUDENT):
        return jsonify({"error": "Invalid Accesss"}), 404
    opp_id = request.args.get('opp_id')
    cur = mysql.connection.cursor()
    resultValue = cur.execute("select * from opportunity where opp_id = %s", (opp_id,))
    if resultValue > 0:
        opportunity_id = cur.fetchone()
        return jsonify(opportunity_id)
    
@app.route('/student')
def get_student_by_id():
    if(USER != Occupation.STUDENT):
        return jsonify({"error": "Invalid Access"}), 404
    stud_id = request.args.get('student_id')
    cur = mysql.connection.cursor()
    resultValue = cur.execute("select * from student where student_id = %s", (stud_id,))
    if resultValue > 0:
        student_id = cur.fetchone()
        return jsonify(student_id)

if __name__ == '__main__':
    app.run(debug=True)

