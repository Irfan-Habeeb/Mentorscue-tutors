from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    class_level = db.Column(db.String(20), nullable=False)  # e.g., "Class 10", "Class 12"
    per_class_fee = db.Column(db.Integer, nullable=False)  # 160, 180, or 200
    assigned_tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.id'), nullable=True)
    subjects = db.Column(db.Text, nullable=False)  # Comma-separated subjects
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    assigned_tutor = db.relationship('Tutor', backref='students')
    
    def get_subjects_list(self):
        return [subject.strip() for subject in self.subjects.split(',') if subject.strip()]

class Tutor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    class_group = db.Column(db.String(50), nullable=False)  # e.g., "10-12", "8-10"
    per_class_pay = db.Column(db.Integer, nullable=False)  # 100, 120, or 140
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    remarks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tutor = db.relationship('Tutor', backref='attendance_records')
    student = db.relationship('Student', backref='attendance_records')
