from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from login_details import details
from flask_cors import CORS

app = Flask(__name__) 

CORS(app)

# App secret key
# Must be the same string present in '__init__.py'
app.secret_key = 'root'

# Must be the same connection present in '__init__.py'
# app.config['SQLALCHEMY_DATABASE_URL']='mysql://username:password@host:port/database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:trongnghia2k1@localhost:3306/project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Tắt thông báo tracking thay đổi
db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(1000))
    admin = db.Column(db.Boolean)


class Students(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)

class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(100))
    filename = db.Column(db.String(100))
    bucket = db.Column(db.String(100))
    region = db.Column(db.String(100))
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = relationship("Users", foreign_keys=[id_user])
    
class Errors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(100))
    filename = db.Column(db.String(100))
    bucket = db.Column(db.String(100))
    region = db.Column(db.String(100))
    editedcontent = db.Column(db.Text)
    errorcontent = db.Column(db.Text)
    status = db.Column(db.Boolean)
    id_file = db.Column(db.Integer, db.ForeignKey('files.id'))
    related_file = relationship("Files", foreign_keys=[id_file])
# 
db.create_all()

def insert_data():
    student_details = details()[0]
    admin_details = details()[1] 
    
    print("Student details")
    
    for email, user_details in student_details.items():
        student = Users.query.filter_by(email=email).first()
        if not student:
            encrypted_password = generate_password_hash(user_details[0])
            new_student = Users(email=email, password=encrypted_password, admin=user_details[1])
            db.session.add(new_student)
            db.session.commit()

    for email, user_details in admin_details.items():
        admin = Users.query.filter_by(email=email).first()
        if not admin:
            encrypted_password = generate_password_hash(user_details[0])
            new_admin = Users(email=email, password=encrypted_password, admin=user_details[1])
            db.session.add(new_admin)
            db.session.commit()

    for email, user_details in student_details.items():
        student = Students.query.filter_by(email=email).first()
        if not student:
            new_student = Students(email=email)
            db.session.add(new_student)
            db.session.commit()

if __name__ == '__main__':
    insert_data()
    