
from datetime import datetime

def safe_parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None
from flask import render_template, request, redirect, url_for, flash, session, make_response, jsonify
from app import app, db
from models import Admin, Student, Tutor, Attendance
from datetime import datetime, date
from utils import generate_parent_invoice, generate_tutor_invoice
import logging
from functools import wraps

logger = logging.getLogger(__name__)

# Admin authentication decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please log in to access the admin dashboard.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('tutor_login'))

# Admin Authentication Routes (Secret URL)
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            flash(f'Welcome back, {admin.username}!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    # Search and filter parameters
    student_search = request.args.get('student_search', '')
    tutor_search = request.args.get('tutor_search', '')
    student_class_filter = request.args.get('student_class_filter', '')
    student_tutor_filter = request.args.get('student_tutor_filter', '')
    tutor_class_filter = request.args.get('tutor_class_filter', '')
    
    # Pagination parameters
    student_page = request.args.get('student_page', 1, type=int)
    tutor_page = request.args.get('tutor_page', 1, type=int)
    per_page = 20
    
    # Build student query
    student_query = Student.query
    if student_search:
        student_query = student_query.filter(Student.name.contains(student_search))
    if student_class_filter:
        student_query = student_query.filter(Student.class_level == student_class_filter)
    if student_tutor_filter:
        student_query = student_query.filter(Student.assigned_tutor_id == student_tutor_filter)
    
    # Build tutor query
    tutor_query = Tutor.query
    if tutor_search:
        tutor_query = tutor_query.filter(Tutor.name.contains(tutor_search))
    if tutor_class_filter:
        tutor_query = tutor_query.filter(Tutor.class_group == tutor_class_filter)
    
    # Get paginated results
    students = student_query.paginate(page=student_page, per_page=per_page, error_out=False)
    tutors = tutor_query.paginate(page=tutor_page, per_page=per_page, error_out=False)
    
    # Get filter options
    all_tutors = Tutor.query.all()
    student_classes = db.session.query(Student.class_level).distinct().all()
    tutor_classes = db.session.query(Tutor.class_group).distinct().all()
    
    total_students = Student.query.count()
    total_tutors = Tutor.query.count()
    total_attendance = Attendance.query.count()
    
    return render_template('admin_dashboard.html', 
                         students=students, 
                         tutors=tutors,
                         all_tutors=all_tutors,
                         student_classes=[c[0] for c in student_classes],
                         tutor_classes=[c[0] for c in tutor_classes],
                         total_students=total_students,
                         total_tutors=total_tutors,
                         total_attendance=total_attendance,
                         student_search=student_search,
                         tutor_search=tutor_search,
                         student_class_filter=student_class_filter,
                         student_tutor_filter=student_tutor_filter,
                         tutor_class_filter=tutor_class_filter)

# Student Management Routes
@app.route('/add_student', methods=['GET', 'POST'])
@admin_required
def add_student():
    if request.method == 'POST':
        try:
            name = request.form['name']
            class_level = request.form['class_level']
            per_class_fee = int(request.form['per_class_fee'])
            assigned_tutor_id = request.form.get('assigned_tutor_id')
            subjects = request.form['subjects']
            
            if assigned_tutor_id == '':
                assigned_tutor_id = None
            else:
                assigned_tutor_id = int(assigned_tutor_id)
            
            student = Student(
                name=name,
                class_level=class_level,
                per_class_fee=per_class_fee,
                assigned_tutor_id=assigned_tutor_id,
                subjects=subjects
            )
            
            db.session.add(student)
            db.session.commit()
            flash('Student added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            logger.error(f"Error adding student: {e}")
            flash('Error adding student. Please try again.', 'error')
    
    tutors = Tutor.query.all()
    return render_template('add_student.html', tutors=tutors)

@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
@admin_required
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    
    if request.method == 'POST':
        try:
            student.name = request.form['name']
            student.class_level = request.form['class_level']
            student.per_class_fee = int(request.form['per_class_fee'])
            assigned_tutor_id = request.form.get('assigned_tutor_id')
            
            if assigned_tutor_id == '':
                student.assigned_tutor_id = None
            else:
                student.assigned_tutor_id = int(assigned_tutor_id)
                
            student.subjects = request.form['subjects']
            
            db.session.commit()
            flash('Student updated successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            logger.error(f"Error updating student: {e}")
            flash('Error updating student. Please try again.', 'error')
    
    tutors = Tutor.query.all()
    return render_template('edit_student.html', student=student, tutors=tutors)

@app.route('/delete_student/<int:student_id>')
@admin_required
def delete_student(student_id):
    try:
        student = Student.query.get_or_404(student_id)
        # Delete associated attendance records
        Attendance.query.filter_by(student_id=student_id).delete()
        db.session.delete(student)
        db.session.commit()
        flash('Student deleted successfully!', 'success')
    except Exception as e:
        logger.error(f"Error deleting student: {e}")
        flash('Error deleting student. Please try again.', 'error')
    
    return redirect(url_for('admin_dashboard'))

# Tutor Management Routes
@app.route('/add_tutor', methods=['GET', 'POST'])
@admin_required
def add_tutor():
    if request.method == 'POST':
        try:
            name = request.form['name']
            class_group = request.form['class_group']
            per_class_pay = int(request.form['per_class_pay'])
            username = request.form['username']
            password = request.form['password']
            
            # Check if username already exists
            existing_tutor = Tutor.query.filter_by(username=username).first()
            if existing_tutor:
                flash('Username already exists. Please choose a different username.', 'error')
                return render_template('add_tutor.html')
            
            tutor = Tutor(
                name=name,
                class_group=class_group,
                per_class_pay=per_class_pay,
                username=username
            )
            tutor.set_password(password)
            
            db.session.add(tutor)
            db.session.commit()
            flash('Tutor added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            logger.error(f"Error adding tutor: {e}")
            flash('Error adding tutor. Please try again.', 'error')
    
    return render_template('add_tutor.html')

@app.route('/edit_tutor/<int:tutor_id>', methods=['GET', 'POST'])
@admin_required
def edit_tutor(tutor_id):
    tutor = Tutor.query.get_or_404(tutor_id)
    
    if request.method == 'POST':
        try:
            tutor.name = request.form['name']
            tutor.class_group = request.form['class_group']
            tutor.per_class_pay = int(request.form['per_class_pay'])
            
            # Check if username changed and if new username exists
            new_username = request.form['username']
            if new_username != tutor.username:
                existing_tutor = Tutor.query.filter_by(username=new_username).first()
                if existing_tutor:
                    flash('Username already exists. Please choose a different username.', 'error')
                    return render_template('edit_tutor.html', tutor=tutor)
                tutor.username = new_username
            
            # Update password if provided
            new_password = request.form.get('password')
            if new_password:
                tutor.set_password(new_password)
            
            db.session.commit()
            flash('Tutor updated successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            logger.error(f"Error updating tutor: {e}")
            flash('Error updating tutor. Please try again.', 'error')
    
    return render_template('edit_tutor.html', tutor=tutor)

@app.route('/delete_tutor/<int:tutor_id>')
@admin_required
def delete_tutor(tutor_id):
    try:
        tutor = Tutor.query.get_or_404(tutor_id)
        # Update students to remove this tutor assignment
        Student.query.filter_by(assigned_tutor_id=tutor_id).update({'assigned_tutor_id': None})
        # Delete associated attendance records
        Attendance.query.filter_by(tutor_id=tutor_id).delete()
        db.session.delete(tutor)
        db.session.commit()
        flash('Tutor deleted successfully!', 'success')
    except Exception as e:
        logger.error(f"Error deleting tutor: {e}")
        flash('Error deleting tutor. Please try again.', 'error')
    
    return redirect(url_for('admin_dashboard'))

# Tutor Login and Attendance Routes
@app.route('/login', methods=['GET', 'POST'])
@app.route('/tutor_login', methods=['GET', 'POST'])
def tutor_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        tutor = Tutor.query.filter_by(username=username).first()
        
        if tutor and tutor.check_password(password):
            session['tutor_id'] = tutor.id
            session['tutor_name'] = tutor.name
            flash(f'Welcome, {tutor.name}!', 'success')
            return redirect(url_for('tutor_submit'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('tutor_login.html')

@app.route('/tutor_logout')
def tutor_logout():
    session.pop('tutor_id', None)
    session.pop('tutor_name', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('tutor_login'))

@app.route('/submit', methods=['GET', 'POST'])
def tutor_submit():
    if 'tutor_id' not in session:
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('tutor_login'))
    
    tutor_id = session['tutor_id']
    tutor = Tutor.query.get_or_404(tutor_id)
    assigned_students = Student.query.filter_by(assigned_tutor_id=tutor_id).all()
    
    if request.method == 'POST':
        try:
            student_id = int(request.form['student_id'])
            subject = request.form['subject']
            attendance_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            remarks = request.form.get('remarks', '')
            
            attendance = Attendance(
                tutor_id=tutor_id,
                student_id=student_id,
                subject=subject,
                date=attendance_date,
                remarks=remarks
            )
            
            db.session.add(attendance)
            db.session.commit()
            flash('Attendance submitted successfully!', 'success')
            return redirect(url_for('tutor_submit'))
        except Exception as e:
            logger.error(f"Error submitting attendance: {e}")
            flash('Error submitting attendance. Please try again.', 'error')
    
    return render_template('tutor_submit.html', 
                         tutor=tutor, 
                         students=assigned_students,
                         today=date.today().strftime('%Y-%m-%d'))

# AJAX route to get student subjects
@app.route('/get_student_subjects/<int:student_id>')
def get_student_subjects(student_id):
    student = Student.query.get_or_404(student_id)
    subjects = student.get_subjects_list()
    return jsonify({'subjects': subjects})

# Student Profile Route
@app.route('/student_profile/<int:student_id>')
@admin_required
def student_profile(student_id):
    student = Student.query.get_or_404(student_id)
    
    # Filter parameters
    subject_filter = request.args.get('subject_filter', '')
    month_filter = request.args.get('month_filter', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    # Build attendance query
    attendance_query = Attendance.query.filter_by(student_id=student_id)
    
    if subject_filter:
        attendance_query = attendance_query.filter(Attendance.subject == subject_filter)
    
    if month_filter:
        year, month = month_filter.split('-')
        from datetime import datetime
        start_month = datetime(int(year), int(month), 1).date()
        if int(month) == 12:
            end_month = datetime(int(year) + 1, 1, 1).date()
        else:
            end_month = datetime(int(year), int(month) + 1, 1).date()
        attendance_query = attendance_query.filter(
            Attendance.date >= start_month,
            Attendance.date < end_month
        )
    elif safe_parse_date(start_date) and safe_parse_date(end_date):
        start = safe_parse_date(start_date)
        end = safe_parse_date(end_date)
        attendance_query = attendance_query.filter(
            Attendance.date >= safe_parse_date(start_date),
            Attendance.date <= safe_parse_date(end_date)
        )
    
    attendance_records = attendance_query.order_by(Attendance.date.desc()).all()
    
    # Group by subject
    subject_attendance = {}
    for record in attendance_records:
        if record.subject not in subject_attendance:
            subject_attendance[record.subject] = []
        subject_attendance[record.subject].append(record)
    
    # Get available subjects and months for filters
    all_subjects = db.session.query(Attendance.subject).filter_by(student_id=student_id).distinct().all()
    available_subjects = [s[0] for s in all_subjects]
    
    return render_template('student_profile.html',
                         student=student,
                         subject_attendance=subject_attendance,
                         attendance_records=attendance_records,
                         available_subjects=available_subjects,
                         subject_filter=subject_filter,
                         month_filter=month_filter,
                         start_date=start_date,
                         end_date=end_date)

# Tutor Profile Route
@app.route('/tutor_profile/<int:tutor_id>')
@admin_required
def tutor_profile(tutor_id):
    tutor = Tutor.query.get_or_404(tutor_id)
    
    # Filter parameters
    subject_filter = request.args.get('subject_filter', '')
    month_filter = request.args.get('month_filter', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    # Build attendance query
    attendance_query = db.session.query(Attendance, Student).join(
        Student, Attendance.student_id == Student.id
    ).filter(Attendance.tutor_id == tutor_id)
    
    if subject_filter:
        attendance_query = attendance_query.filter(Attendance.subject == subject_filter)
    
    if month_filter:
        year, month = month_filter.split('-')
        from datetime import datetime
        start_month = datetime(int(year), int(month), 1).date()
        if int(month) == 12:
            end_month = datetime(int(year) + 1, 1, 1).date()
        else:
            end_month = datetime(int(year), int(month) + 1, 1).date()
        attendance_query = attendance_query.filter(
            Attendance.date >= start_month,
            Attendance.date < end_month
        )
    elif safe_parse_date(start_date) and safe_parse_date(end_date):
        start = safe_parse_date(start_date)
        end = safe_parse_date(end_date)
        attendance_query = attendance_query.filter(
            Attendance.date >= safe_parse_date(start_date),
            Attendance.date <= safe_parse_date(end_date)
        )
    
    attendance_records = attendance_query.order_by(Attendance.date.desc()).all()
    
    # Get available subjects for filters
    all_subjects = db.session.query(Attendance.subject).filter_by(tutor_id=tutor_id).distinct().all()
    available_subjects = [s[0] for s in all_subjects]
    
    return render_template('tutor_profile.html',
                         tutor=tutor,
                         attendance_records=attendance_records,
                         available_subjects=available_subjects,
                         subject_filter=subject_filter,
                         month_filter=month_filter,
                         start_date=start_date,
                         end_date=end_date)

# Attendance Management Routes
@app.route('/view_attendance')
@admin_required
def view_attendance():
    attendance_records = db.session.query(Attendance, Student, Tutor).join(
        Student, Attendance.student_id == Student.id
    ).join(
        Tutor, Attendance.tutor_id == Tutor.id
    ).order_by(Attendance.date.desc()).all()
    
    return render_template('view_attendance.html', attendance_records=attendance_records)

@app.route('/delete_attendance/<int:attendance_id>')
@admin_required
def delete_attendance(attendance_id):
    try:
        attendance = Attendance.query.get_or_404(attendance_id)
        db.session.delete(attendance)
        db.session.commit()
        flash('Attendance record deleted successfully!', 'success')
    except Exception as e:
        logger.error(f"Error deleting attendance: {e}")
        flash('Error deleting attendance record. Please try again.', 'error')
    
    return redirect(url_for('view_attendance'))

@app.route('/delete_all_attendance/<int:tutor_id>')
@admin_required
def delete_all_attendance(tutor_id):
    try:
        Attendance.query.filter_by(tutor_id=tutor_id).delete()
        db.session.commit()
        flash('All attendance records for this tutor deleted successfully!', 'success')
    except Exception as e:
        logger.error(f"Error deleting all attendance: {e}")
        flash('Error deleting attendance records. Please try again.', 'error')
    
    return redirect(url_for('view_attendance'))

# PDF Invoice Routes
@app.route('/generate_parent_invoice/<int:student_id>')
@admin_required
def generate_parent_invoice(student_id):
    try:
        student = Student.query.get_or_404(student_id)
        
        # Get filter parameters for filtered invoice
        subject_filter = request.args.get('subject_filter', '')
        month_filter = request.args.get('month_filter', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        pdf_buffer = generate_parent_invoice(student, subject_filter, month_filter, start_date, end_date)
        
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        
        # Add filter info to filename
        filename_suffix = ""
        if month_filter:
            filename_suffix = f"_{month_filter}"
        elif start_date and end_date:
            filename_suffix = f"_{start_date}_to_{end_date}"
        
        response.headers['Content-Disposition'] = f'attachment; filename=parent_invoice_{student.name.replace(" ", "_")}{filename_suffix}.pdf'
        
        return response
    except Exception as e:
        logger.error(f"Error generating parent invoice: {e}")
        flash('Error generating invoice. Please try again.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/generate_tutor_invoice/<int:tutor_id>')
@admin_required
def generate_tutor_invoice(tutor_id):
    try:
        tutor = Tutor.query.get_or_404(tutor_id)
        
        # Get filter parameters for filtered invoice
        subject_filter = request.args.get('subject_filter', '')
        month_filter = request.args.get('month_filter', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        pdf_buffer = generate_tutor_invoice(tutor, subject_filter, month_filter, start_date, end_date)
        
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        
        # Add filter info to filename
        filename_suffix = ""
        if month_filter:
            filename_suffix = f"_{month_filter}"
        elif start_date and end_date:
            filename_suffix = f"_{start_date}_to_{end_date}"
        
        response.headers['Content-Disposition'] = f'attachment; filename=tutor_invoice_{tutor.name.replace(" ", "_")}{filename_suffix}.pdf'
        
        return response
    except Exception as e:
        logger.error(f"Error generating tutor invoice: {e}")
        flash('Error generating invoice. Please try again.', 'error')
        return redirect(url_for('admin_dashboard'))
