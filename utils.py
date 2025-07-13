from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from models import Attendance, Student
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def generate_parent_invoice(student, subject_filter='', month_filter='', start_date='', end_date=''):
    """Generate PDF invoice for parents showing subject-wise breakdown"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#344e80')
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#344e80')
    )
    
    # Title
    story.append(Paragraph("MentorsCue", title_style))
    story.append(Paragraph("Student Invoice", header_style))
    story.append(Spacer(1, 20))
    
    # Student Information
    story.append(Paragraph(f"<b>Student Name:</b> {student.name}", styles['Normal']))
    story.append(Paragraph(f"<b>Class:</b> {student.class_level}", styles['Normal']))
    story.append(Paragraph(f"<b>Per Class Fee:</b> ₹{student.per_class_fee}", styles['Normal']))
    if student.assigned_tutor:
        story.append(Paragraph(f"<b>Assigned Tutor:</b> {student.assigned_tutor.name}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Get attendance records for this student with filters
    attendance_query = Attendance.query.filter_by(student_id=student.id)
    
    if subject_filter:
        attendance_query = attendance_query.filter(Attendance.subject == subject_filter)
    
    if month_filter:
        from datetime import datetime
        year, month = month_filter.split('-')
        start_month = datetime(int(year), int(month), 1).date()
        if int(month) == 12:
            end_month = datetime(int(year) + 1, 1, 1).date()
        else:
            end_month = datetime(int(year), int(month) + 1, 1).date()
        attendance_query = attendance_query.filter(
            Attendance.date >= start_month,
            Attendance.date < end_month
        )
    elif start_date and end_date:
        from datetime import datetime
        attendance_query = attendance_query.filter(
            Attendance.date >= datetime.strptime(start_date, '%Y-%m-%d').date(),
            Attendance.date <= datetime.strptime(end_date, '%Y-%m-%d').date()
        )
    
    attendance_records = attendance_query.all()
    
    if attendance_records:
        # Subject-wise breakdown
        subject_counts = {}
        for record in attendance_records:
            if record.subject in subject_counts:
                subject_counts[record.subject] += 1
            else:
                subject_counts[record.subject] = 1
        
        # Create table data
        table_data = [['Subject', 'Classes Attended', 'Fee per Class', 'Total Amount']]
        total_amount = 0
        
        for subject, count in subject_counts.items():
            amount = count * student.per_class_fee
            total_amount += amount
            table_data.append([
                subject,
                str(count),
                f'₹{student.per_class_fee}',
                f'₹{amount}'
            ])
        
        # Add total row
        table_data.append(['', '', '<b>Total:</b>', f'<b>₹{total_amount}</b>'])
        
        # Create table
        table = Table(table_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#344e80')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#cedce7')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
    else:
        story.append(Paragraph("No attendance records found for this student.", styles['Normal']))
    
    story.append(Spacer(1, 40))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2e3a4d')
    )
    story.append(Paragraph("Powered by MentorsCue — Online Tuition & Mentorship", footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_tutor_invoice(tutor, subject_filter='', month_filter='', start_date='', end_date=''):
    """Generate PDF invoice for tutors showing class details and salary"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#344e80')
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#344e80')
    )
    
    # Title
    story.append(Paragraph("MentorsCue", title_style))
    story.append(Paragraph("Tutor Invoice", header_style))
    story.append(Spacer(1, 20))
    
    # Tutor Information
    story.append(Paragraph(f"<b>Tutor Name:</b> {tutor.name}", styles['Normal']))
    story.append(Paragraph(f"<b>Class Group:</b> {tutor.class_group}", styles['Normal']))
    story.append(Paragraph(f"<b>Per Class Pay:</b> ₹{tutor.per_class_pay}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Get attendance records for this tutor with filters
    attendance_query = Attendance.query.filter_by(tutor_id=tutor.id)
    
    if subject_filter:
        attendance_query = attendance_query.filter(Attendance.subject == subject_filter)
    
    if month_filter:
        from datetime import datetime
        year, month = month_filter.split('-')
        start_month = datetime(int(year), int(month), 1).date()
        if int(month) == 12:
            end_month = datetime(int(year) + 1, 1, 1).date()
        else:
            end_month = datetime(int(year), int(month) + 1, 1).date()
        attendance_query = attendance_query.filter(
            Attendance.date >= start_month,
            Attendance.date < end_month
        )
    elif start_date and end_date:
        from datetime import datetime
        attendance_query = attendance_query.filter(
            Attendance.date >= datetime.strptime(start_date, '%Y-%m-%d').date(),
            Attendance.date <= datetime.strptime(end_date, '%Y-%m-%d').date()
        )
    
    attendance_records = attendance_query.all()
    
    if attendance_records:
        # Create table data
        table_data = [['Date', 'Student', 'Subject', 'Pay', 'Remarks']]
        total_salary = 0
        
        for record in attendance_records:
            total_salary += tutor.per_class_pay
            table_data.append([
                record.date.strftime('%Y-%m-%d'),
                record.student.name,
                record.subject,
                f'₹{tutor.per_class_pay}',
                record.remarks or '-'
            ])
        
        # Add total row
        table_data.append(['', '', '', f'<b>Total: ₹{total_salary}</b>', ''])
        
        # Create table
        table = Table(table_data, colWidths=[1*inch, 2*inch, 1.5*inch, 1*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#344e80')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#cedce7')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Summary
        story.append(Paragraph(f"<b>Total Classes Conducted:</b> {len(attendance_records)}", styles['Normal']))
        story.append(Paragraph(f"<b>Total Salary Earned:</b> ₹{total_salary}", styles['Normal']))
    else:
        story.append(Paragraph("No attendance records found for this tutor.", styles['Normal']))
    
    story.append(Spacer(1, 40))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2e3a4d')
    )
    story.append(Paragraph("Powered by MentorsCue — Online Tuition & Mentorship", footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer
