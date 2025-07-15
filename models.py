from app import db
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import and_, func

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
    parent_name = db.Column(db.String(100), nullable=False)
    class_level = db.Column(db.String(20), nullable=False)  # e.g., "Class 10", "Class 12"
    per_class_fee = db.Column(db.Integer, nullable=False)  # Manual entry now
    subjects = db.Column(db.Text, nullable=False)  # Comma-separated subjects
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_payment_date = db.Column(db.Date, nullable=True)
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, partial, overdue
    
    # Relationships
    tutor_links = db.relationship('StudentTutorLink', back_populates='student', cascade='all, delete-orphan')
    
    def get_subjects_list(self):
        return [subject.strip() for subject in self.subjects.split(',') if subject.strip()]
    
    def get_total_classes(self, start_date=None, end_date=None):
        query = Attendance.query.filter(Attendance.student_id == self.id)
        if start_date:
            query = query.filter(Attendance.date >= start_date)
        if end_date:
            query = query.filter(Attendance.date <= end_date)
        return query.count()
    
    def get_total_fee_due(self, start_date=None, end_date=None):
        total_classes = self.get_total_classes(start_date, end_date)
        return total_classes * self.per_class_fee

class Tutor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    class_group = db.Column(db.String(50), nullable=False)  # e.g., "10-12", "8-10"
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)  # For GPay
    payment_details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_payment_date = db.Column(db.Date, nullable=True)
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, partial, overdue
    
    # Relationships
    student_links = db.relationship('StudentTutorLink', back_populates='tutor', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_total_classes(self, start_date=None, end_date=None):
        query = Attendance.query.filter(Attendance.tutor_id == self.id)
        if start_date:
            query = query.filter(Attendance.date >= start_date)
        if end_date:
            query = query.filter(Attendance.date <= end_date)
        return query.count()
    
    def get_total_earnings(self, start_date=None, end_date=None):
        total = 0
        query = Attendance.query.filter(Attendance.tutor_id == self.id)
        if start_date:
            query = query.filter(Attendance.date >= start_date)
        if end_date:
            query = query.filter(Attendance.date <= end_date)
        
        for attendance in query.all():
            link = StudentTutorLink.query.filter_by(
                student_id=attendance.student_id,
                tutor_id=self.id
            ).first()
            if link:
                total += link.pay_per_class
        return total

class StudentTutorLink(db.Model):
    """Association table for student-tutor relationships with custom pay rates"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.id'), nullable=False)
    pay_per_class = db.Column(db.Integer, nullable=False)  # Custom pay rate for this tutor-student pair
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', back_populates='tutor_links')
    tutor = db.relationship('Tutor', back_populates='student_links')
    
    # Ensure unique student-tutor pairs
    __table_args__ = (db.UniqueConstraint('student_id', 'tutor_id', name='unique_student_tutor'),)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-10 scale
    remarks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tutor = db.relationship('Tutor', backref='attendance_records')
    student = db.relationship('Student', backref='attendance_records')
    
    def get_duration_minutes(self):
        """Calculate class duration in minutes"""
        start_datetime = datetime.combine(date.today(), self.start_time)
        end_datetime = datetime.combine(date.today(), self.end_time)
        duration = end_datetime - start_datetime
        return int(duration.total_seconds() / 60)
