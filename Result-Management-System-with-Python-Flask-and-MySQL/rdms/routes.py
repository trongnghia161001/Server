from flask import render_template, redirect, url_for, flash, jsonify, send_file, request, session
from werkzeug.security import check_password_hash
from flask_login import login_required, login_user, logout_user
from flask_login import current_user

from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

from rdms import db, app 
from rdms.models import Users 
from rdms.models import Files
from flask import Flask, request
from werkzeug.utils import secure_filename
import os
from time import time
import os
import boto3
import uuid
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import socket
import json
import websockets
import asyncio

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# App home page
@app.route('/')
def index():
    return render_template('home.html')


# Handle student and admin login
@app.route('/login', methods=['POST', 'GET']) 
def login():
    """Handle user login and authenticate inputs."""
    # Check if username and password requests exist
    if request.method == "POST":
        # At first assume the user is a student 
        student_email = request.form.get('student_email')
        # If student_email from home.html is not 'None' then user is a student

        if student_email:
            # Query Users table against student email and password
            student_password = request.form.get('student_password')
            student = Users.query.filter_by(email=student_email).first()
            # Check if the student email is valid along with the password  
            
            if (student and 
                check_password_hash(student.password, student_password) and 
                student_email.endswith('stu.edu.ng')):
                # Login user as student and set remember me attribute to true
                login_user(student, remember=True) 
                session['user_id'] = student.id
                print(session['user_id'])
                # Redirect student to the result page
                return redirect(url_for('result')) 
            # Display message if login details are incorrect
            else:
                flash('Invalid Student Email or Password') 
                return redirect(url_for('index')) 
        # If Boolean of 'student_email' is False then validate user as an admin
        else:
            # Query Users table against admin email and password
            admin_email = request.form.get('admin_email')
            admin_password = request.form.get('admin_password')
            admin = Users.query.filter_by(email=admin_email).first()
            # Check if admin account is valid

            if admin and check_password_hash(admin.password, admin_password):
                login_user(admin, remember=True)
                return redirect(url_for('admin.index')) 
            # Display message if account details does not exist
            else:
                flash('Invalid Login Details. Retry') 
                return redirect(url_for('index')) 

    else:
        # If request method is not POST redirect to home page
        return redirect(url_for('index')) 


@app.route('/about')
def about():
    """Render about.html file."""
    return render_template('about.html')


@app.route('/contact')
def contact():
    """Render contact.html file."""
    return render_template('contact.html')


@app.route('/details')
def details():
    """Render details.html file."""
    return render_template('details.html')


@app.route('/result')
@login_required
def result():
    """Render result.html file"""
    user_id = current_user.id
    # Query 'profiles' table for KẾT QUẢ details
    profile_info = db.engine.execute(
        f"SELECT * FROM `files` WHERE id_user = '{user_id}'"
    ) 
    # Query 'results' table for distinct student results
    student_result = db.engine.execute(
        f"SELECT * FROM `files` WHERE id_user = '{user_id}'"
    ) 

    return render_template(
        'result.html', 
        profile_info=profile_info, 
        student_result=student_result
    )


# Handle page not found error (404)
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html')  


@app.route('/logout')
def logout():
    """Logout user and redirect to home page"""
    logout_user()
    return redirect(url_for('index')) 

app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'files')


import os
import boto3
from flask import request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import uuid

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        uploaded_file = request.files["file"]
        if not allowed_file(uploaded_file.filename):
            return "FILE NOT ALLOWED!"

        user_id = current_user.id
        file_extension = uploaded_file.filename.rsplit('.', 1)[1].lower() 
        new_filename = f"{user_id}_{uuid.uuid4().hex}.{file_extension}"
        bucket_name = "laptrinhmangnangcao"

        s3 = boto3.resource("s3", aws_access_key_id="AKIA5IACU6HRNBHF4AWX", aws_secret_access_key="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")
        bucket = s3.Bucket(bucket_name)

        # Kiểm tra xem object có tồn tại hay không
        for obj in bucket.objects.filter(Prefix=f"{user_id}_"):
            if obj.key.split("_")[0] == str(user_id):
        # Nếu tồn tại, xóa file cũ
                s3.Object(bucket_name, obj.key).delete()
                break


        # Tải file mới lên bucket
        bucket.upload_fileobj(uploaded_file, new_filename)

        file = Files(
            original_filename=new_filename,
            filename=uploaded_file.filename,
            bucket=bucket_name,
            region="ap-southeast-1",
            id_user=user_id
        )
        db.session.add(file)
        db.session.commit()

        return redirect(url_for("result"))

    files = Files.query.all()
    return render_template("result.html", files=files)


@app.route("/check", methods=["POST"])
def send_data():
    user_id = current_user.id
    return str(user_id)

        

# @app.route("/download/<filename>", methods=['GET'])
# def download(filename):
#     if request.method == 'GET':
#         output = download_file(filename, BUCKET)
# 
#         return send_file(output, as_attachment=True)

# @app.route("/check", methods=["POST"])
# def check():
#     try:
#         user_id = current_user.id
#         server2_address = ('127.0.0.1', 8080)  # Server2 IP and a different port
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#             try:
#                 s.connect(server2_address)
#                 user_data = {'user_id': user_id}  # Convert data to a JSON object
#                 user_json = json.dumps(user_data).encode('utf-8')  # Encode data to JSON
#                 data_length = len(user_json).to_bytes(4, byteorder='big')  # Encode data length
#                 s.sendall(data_length + user_json)  # Send data to Server2
#                 return "Data sent to Server2"
#             except ConnectionRefusedError:
#                 return jsonify({"error": "Connection to Server2 refused"})
#     except Exception as e:
#         return jsonify({"error": "An error occurred"})
        

