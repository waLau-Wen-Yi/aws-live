from crypt import methods
import re
from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *
import datetime

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb
)

output = {}                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    

#@@@@@@@@@@General
@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('Home.html')

@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')

#@@@@@@@@@@Employee Management
@app.route("/empmng", methods=['GET', 'POST'])
def EmpMng():
    return render_template('/EmpMng/EmpMngHome.html')


@app.route("/rgsemp", methods=['GET', 'POST'])
def RgsEmp():
    return render_template('/EmpMng/RegisEmp.html')

@app.route("/addemp", methods=['POST'])
def AddEmp():
        emp_fname = request.form['emp_fname']
        emp_lname = request.form['emp_lname']
        emp_position = request.form['emp_position']
        emp_id = request.form['emp_id']
        emp_phone = request.form['emp_phone']
        emp_email = request.form['emp_email']
        emp_jdate = datetime.date.today()
        emp_salary = request.form['emp_salary']
        emp_location = request.form['emp_location']
        emp_interest = request.form['emp_interest']
        emp_dob = request.form['emp_dob']
        emp_skills = request.form['emp_skills']
        emp_image_file = request.files['image_file']

        insert_sql = "INSERT INTO employee (id, fname, lname, position, phone, email, jdate, salary, location, interest, dob, skills) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()

        if emp_image_file.filename == "":
            return "Please select a file"

        try:
            cursor.execute(insert_sql, 
                (emp_id, emp_fname, emp_lname,
                emp_position, emp_phone, emp_email, emp_jdate,
                emp_salary, emp_location, emp_interest, emp_dob,
                emp_skills))
            db_conn.commit()
            # Uplaod image file in S3 #
            emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_profile_pic"
            s3 = boto3.resource('s3')

            try:
                print("Data inserted in MySQL RDS... uploading image to S3...")
                s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
                bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                s3_location = (bucket_location['LocationConstraint'])

                if s3_location is None:
                    s3_location = ''
                else:
                    s3_location = '-' + s3_location

                object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                    s3_location,
                    custombucket,
                    emp_image_file_name_in_s3)

                cursor.execute("UPDATE employee SET imgurl = (%s) WHERE id = (%s)", object_url, emp_id)
                db_conn.commit()

            except Exception as e:
                return str(e)

        finally:
            cursor.close()

        print("all modification done...")
        return render_template('/EmpMng/ShowEmpDetails.html', 
             id = emp_id, 
             imgurl = object_url,
             fname = emp_fname,
             lname = emp_lname,
             position = emp_position,
             phone = emp_phone,
             email = emp_email,
             jdate = emp_jdate,
             salary = emp_salary,
             location = emp_location,
             interest = emp_interest,
             dob = emp_dob,
             skills = emp_skills
             )

@app.route("/shwempdtl", methods=['GET', 'POST'])
def ShwEmpDtl():
    routePage = "/EmpMng/ShowEmpDetails.html"
    emp_id = 0
    empData = []
    cursor = db_conn.cursor()
    if (request.method == 'GET'):
        emp_id = request.args['emp_id']
        qryRslt = cursor.execute("SELECT * FROM employee WHERE id = (%s)", (emp_id))
        if qryRslt == 0:
            return render_template(routePage, id = "DOES NOT EXISTED, PLEASE SEARCH ANOTHER ID")
        else:
            empData = cursor.fetchall()
            return render_template(routePage,
             id = empData[0][0], 
             fname = empData[0][2],
             lname = empData[0][3],
             position = empData[0][4],
             phone = empData[0][5],
             email = empData[0][6],
             jdate = empData[0][7],
             salary = empData[0][8],
             location = empData[0][9],
             interest = empData[0][10],
             dob = empData[0][11],
             skills = empData[0][12]
             )
    return render_template(routePage, id = "")

@app.route("/edtempdtl", methods=['GET', 'POST'])
def EdtEmpDtl():
    routePage = "/EmpMng/EditEmpDetails.html"
    cursor = db_conn.cursor()
    if (request.method == 'GET'):
        emp_id = request.args['emp_id']
        qryRslt = cursor.execute("SELECT * FROM employee WHERE id = (%s)", (emp_id))
        if qryRslt == 0:
            return render_template(routePage, id = "DATA NOT FOUNDED, PLEASE SEARCH ANOTHER ID")
        else:
            empData = cursor.fetchall()
            return render_template(routePage,
             id = empData[0][0], 
             fname = empData[0][2],
             lname = empData[0][3],
             position = empData[0][4],
             phone = empData[0][5],
             email = empData[0][6],
             jdate = empData[0][7],
             salary = empData[0][8],
             location = empData[0][9],
             interest = empData[0][10],
             dob = empData[0][11],
             skills = empData[0][12]
             )
    return render_template(routePage)

@app.route('/edtemp', methods=['POST'])
def EdtEmp():
    emp_fname = request.form['emp_fname']
    emp_lname = request.form['emp_lname']
    emp_position = request.form['emp_position']
    emp_id = request.form['emp_id']
    emp_phone = request.form['emp_phone']
    emp_email = request.form['emp_email']
    emp_jdate = request.form['emp_jdate']
    emp_salary = request.form['emp_salary']
    emp_location = request.form['emp_location']
    emp_interest = request.form['emp_interest']
    emp_dob = request.form['emp_dob']
    emp_skills = request.form['emp_skills']

    cursor = db_conn.cursor()
    cursor.execute(
        "UPDATE employee SET fname = (%s), lname = (%s), position = (%s), phone = (%s), email = (%s), jdate = (%s), salary = (%s), location = (%s), interest = (%s), dob = (%s), skills = (%s) WHERE id = (%s)",
        (emp_fname, emp_lname, emp_position, emp_phone, emp_email, emp_jdate, emp_salary, emp_location, emp_interest, emp_dob, emp_skills, emp_id))
    db_conn.commit()

    routePage = "/EmpMng/EditEmpDetails.html"
    qryRslt = cursor.execute("SELECT * FROM employee WHERE id = (%s)", (emp_id))
    empData = cursor.fetchall()
    return render_template(routePage,
        id = empData[0][0], 
        fname = empData[0][2],
        lname = empData[0][3],
        position = empData[0][4],
        phone = empData[0][5],
        email = empData[0][6],
        jdate = empData[0][7],
        salary = empData[0][8],
        location = empData[0][9],
        interest = empData[0][10],
        dob = empData[0][11],
        skills = empData[0][12]
        )

@app.route('/rmvemp', methods=['GET', 'POST'])
def RmvEmp():
    routePage = "/EmpMng/RemoveEmp.html"
    cursor = db_conn.cursor()
    if (request.method == 'GET'):
        emp_id = request.args['emp_id']
        qryRslt = cursor.execute("SELECT * FROM employee WHERE id = (%s)", (emp_id))
        if qryRslt == 0:
            return render_template(routePage, id = "DATA NOT FOUNDED, PLEASE SEARCH ANOTHER ID")
        else:
            empData = cursor.fetchall()
            return render_template(routePage,
             id = empData[0][0],
             fname = empData[0][2],
             lname = empData[0][3],
             position = empData[0][4],
             jdate = empData[0][7]
             )
    return render_template(routePage)

@app.route('/rmvempcmfrm', methods=['GET'])
def RmvEmpCmfrm():
    routePage = "/EmpMng/RemoveEmp.html"
    cursor = db_conn.cursor()
    emp_id = request.args['emp_id']
    qryRslt = cursor.execute("DELETE FROM employee WHERE id = %s", (emp_id))
    if qryRslt == 1:
        return render_template(routePage, id = "ID ({}) HAS BEEN DELETED".format(emp_id))
    else:
        return render_template(routePage, id = "SOMETHING IS WRONG")

#@@@@@@@@@@Performance Tracker
@app.route('/prftrk', methods=['GET', 'POST'])
def PrfTrk():
    routePage = "/PrfTrk/PrfTrk.html"
    cursor = db_conn.cursor()
    if (request.method == 'GET'):
        emp_id = request.args['emp_id']
        qryRslt = cursor.execute("SELECT * FROM employee WHERE id = (%s)", (emp_id))
        if qryRslt == 0:
            return render_template(routePage, id = "DATA NOT FOUNDED, PLEASE SEARCH ANOTHER ID")
        else:
            empData = cursor.fetchall()
            goal_id = 'prf{}'.format(emp_id)
            qryRslt = cursor.execute("SELECT * FROM performance WHERE prf_id = %s", (goal_id))
            if (qryRslt == 1):
                prfData = cursor.fetchall()
                return render_template(routePage,
                id = empData[0][0],
                fname = empData[0][2],
                lname = empData[0][3],
                position = empData[0][4],
                jdate = empData[0][7],
                goal = prfData[0][1],
                objective = prfData[0][2],
                grade = prfData[0][3],
                pros = prfData[0][4],
                cons = prfData[0][5]
                )
            else:
                return render_template(routePage,
                id = empData[0][0],
                fname = empData[0][2],
                lname = empData[0][3],
                position = empData[0][4],
                jdate = empData[0][7],
                goal = "DATA NOT FOUNDED"
                )
    return render_template(routePage)

@app.route('/prftrkedt', methods=['GET'])
def PrfTrkEdt():
    routePage = "/PrfTrk/PrfTrkEdt.html"
    cursor = db_conn.cursor()
    emp_id = request.args['emp_id']
    qryRslt = cursor.execute("SELECT * FROM employee WHERE id = (%s)", (emp_id))
    if qryRslt == 0:
        return render_template(routePage, id = "DATA NOT FOUNDED, PLEASE SEARCH ANOTHER ID")
    else:
        empData = cursor.fetchall()
        goal_id = 'prf{}'.format(emp_id)
        qryRslt = cursor.execute("SELECT * FROM performance WHERE prf_id = %s", (goal_id))
        if (qryRslt == 1):
            prfData = cursor.fetchall()
            return render_template(routePage,
            id = empData[0][0],
            fname = empData[0][2],
            lname = empData[0][3],
            position = empData[0][4],
            jdate = empData[0][7],
            goal = prfData[0][1],
            objective = prfData[0][2],
            grade = prfData[0][3],
            pros = prfData[0][4],
            cons = prfData[0][5]
            )
        else:
            return render_template(routePage,
            id = empData[0][0],
            fname = empData[0][2],
            lname = empData[0][3],
            position = empData[0][4],
            jdate = empData[0][7],
            goal = "DATA NOT FOUNDED"
            )

@app.route('/prfedtact', methods=['POST'])
def PrfEdtAct():
    routePage = "/PrfTrk/PrfTrk.html"
    cursor = db_conn.cursor()
    emp_id = request.form['emp_id']
    goal_id = request.form['prf_id']
    goal = request.form['prf_goal']
    objective = request.form['prf_obj']
    grade = request.form['prf_grade']
    pros = request.form['prf_pros']
    cons = request.form['prf_cons']
    cursor.execute(
        "UPDATE performance SET prf_goal = (%s), prf_obj = (%s), prf_grade = (%s), prf_pros = (%s), prf_cons = (%s) WHERE prf_id = (%s)",
        (goal, objective, grade, pros, cons, goal_id))
    db_conn.commit()

    qryRslt = cursor.execute("SELECT * FROM employee WHERE id = (%s)", (emp_id))
    if qryRslt == 0:
        return render_template(routePage, id = "DATA NOT FOUNDED, PLEASE SEARCH ANOTHER ID")
    else:
        empData = cursor.fetchall()
        goal_id = 'prf{}'.format(emp_id)
        qryRslt = cursor.execute("SELECT * FROM performance WHERE prf_id = %s", (goal_id))
        if (qryRslt == 1):
            prfData = cursor.fetchall()
            return render_template(routePage,
            id = empData[0][0],
            fname = empData[0][2],
            lname = empData[0][3],
            position = empData[0][4],
            jdate = empData[0][7],
            goal = prfData[0][1],
            objective = prfData[0][2],
            grade = prfData[0][3],
            pros = prfData[0][4],
            cons = prfData[0][5]
            )
        else:
            return render_template(routePage,
            id = empData[0][0],
            fname = empData[0][2],
            lname = empData[0][3],
            position = empData[0][4],
            jdate = empData[0][7],
            goal = "DATA NOT FOUNDED"
            )

#DON'T TOUCH!
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
