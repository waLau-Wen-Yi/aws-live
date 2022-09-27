from crypt import methods
import re
from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

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
@app.route("/shwempdtl", methods=['GET', 'POST'])
def ShwEmpDtl():
    routePage = "/EmpMng/[!]ShowEmpDetails.html"
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
    cursor = db_conn.cursor()
    if (request.method == 'POST'):
        return render_template("/EmpMng/[!]ShowEmpDetails.html", id = "DATA NOT FOUNDED, PLEASE SEARCH ANOTHER ID")
    if (request.method == 'GET'):
        routePage = "/EmpMng/[!]EditEmpDetails.html"
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
    return render_template(routePage, id = "")

#
    @app.route("/addemp", methods=['POST'])
    def AddEmp():
        emp_id = request.form['emp_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        pri_skill = request.form['pri_skill']
        location = request.form['location']
        emp_image_file = request.files['emp_image_file']

        insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()

        if emp_image_file.filename == "":
            return "Please select a file"

        try:

            cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
            db_conn.commit()
            emp_name = "" + first_name + " " + last_name
            # Uplaod image file in S3 #
            emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
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

            except Exception as e:
                return str(e)

        finally:
            cursor.close()

        print("all modification done...")
        return render_template('AddEmpOutput.html', name=emp_name)

#@@@@@@@@@@Performance Tracker


#DON'T TOUCH!
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
