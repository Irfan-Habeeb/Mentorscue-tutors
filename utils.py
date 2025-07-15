from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from models import Attendance
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_parent_invoice(student, subject_filter='', month_filter='', start_date='', end_date=''):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#344e80'),
        spaceAfter=20
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#344e80'),
        spaceAfter=10
    )
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2e3a4d')
    )

    # Header
    story.append(Paragraph("MENTORSCUE", title_style))
    story.append(Paragraph("Student Invoice", subtitle_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"<b>Student Name:</b> {student.name}", styles['Normal']))
    story.append(Paragraph(f"<b>Parent Name:</b> {student.parent_name}", styles['Normal']))
    story.append(Paragraph(f"<b>Class:</b> {student.class_level}", styles['Normal']))
    story.append(Paragraph(f"<b>Per Class Fee:</b> Rs.{student.per_class_fee}", styles['Normal']))
    
    # Display assigned tutors (multi-tutor support)
    tutor_names = []
    for link in student.tutor_links:
        tutor_names.append(f"{link.tutor.name} (₹{link.pay_per_class} per class)")
    if tutor_names:
        story.append(Paragraph(f"<b>Assigned Tutors:</b> {', '.join(tutor_names)}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Query attendance
    attendance_query = Attendance.query.filter_by(student_id=student.id)
    if subject_filter:
        attendance_query = attendance_query.filter(Attendance.subject == subject_filter)
    if month_filter:
        year, month = map(int, month_filter.split('-'))
        start = datetime(year, month, 1).date()
        end = datetime(year + int(month == 12), (month % 12) + 1, 1).date()
        attendance_query = attendance_query.filter(Attendance.date >= start, Attendance.date < end)
    elif start_date and end_date:
        attendance_query = attendance_query.filter(
            Attendance.date >= datetime.strptime(start_date, '%Y-%m-%d').date(),
            Attendance.date <= datetime.strptime(end_date, '%Y-%m-%d').date()
        )
    
    records = attendance_query.all()

    if records:
        subject_counts = {}
        for rec in records:
            subject_counts[rec.subject] = subject_counts.get(rec.subject, 0) + 1

        data = [['Subject', 'Classes Attended', 'Fee per Class', 'Total']]
        total_fee = 0
        for subject, count in subject_counts.items():
            total = count * student.per_class_fee
            total_fee += total
            data.append([subject, str(count), f'Rs.{student.per_class_fee}', f'Rs.{total}'])

        data.append(['', '', 'TOTAL:', f'Rs.{total_fee}'])

        table = Table(data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#344e80')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#cedce7'))
        ]))
        story.append(table)
    else:
        story.append(Paragraph("No attendance records found for this student.", styles['Normal']))

    story.append(Spacer(1, 20))
    story.append(Paragraph("Powered by Mentorscue Online Tuition", footer_style))
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_tutor_invoice(tutor, subject_filter='', month_filter='', start_date='', end_date=''):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#344e80'),
        spaceAfter=20
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#344e80'),
        spaceAfter=10
    )
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2e3a4d')
    )

    # Header
    story.append(Paragraph("Mentorscue", title_style))
    story.append(Paragraph("Tutor Invoice", subtitle_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"<b>Tutor Name:</b> {tutor.name}", styles['Normal']))
    story.append(Paragraph(f"<b>Class Group:</b> {tutor.class_group}", styles['Normal']))
    story.append(Paragraph(f"<b>Mobile Number:</b> {tutor.mobile_number}", styles['Normal']))
    story.append(Spacer(1, 12))

    attendance_query = Attendance.query.filter_by(tutor_id=tutor.id)
    if subject_filter:
        attendance_query = attendance_query.filter(Attendance.subject == subject_filter)
    if month_filter:
        year, month = map(int, month_filter.split('-'))
        start = datetime(year, month, 1).date()
        end = datetime(year + int(month == 12), (month % 12) + 1, 1).date()
        attendance_query = attendance_query.filter(Attendance.date >= start, Attendance.date < end)
    elif start_date and end_date:
        attendance_query = attendance_query.filter(
            Attendance.date >= datetime.strptime(start_date, '%Y-%m-%d').date(),
            Attendance.date <= datetime.strptime(end_date, '%Y-%m-%d').date()
        )
    
    records = attendance_query.all()

    if records:
        from models import StudentTutorLink
        
        data = [['Date', 'Student', 'Subject', 'Pay', 'Remarks']]
        total_salary = 0
        for r in records:
            # Get the specific pay rate for this tutor-student pair
            link = StudentTutorLink.query.filter_by(
                student_id=r.student_id,
                tutor_id=tutor.id
            ).first()
            pay_for_class = link.pay_per_class if link else 100  # Default pay if no link found
            total_salary += pay_for_class
            
            data.append([
                r.date.strftime('%Y-%m-%d'),
                r.student.name,
                r.subject,
                f'Rs.{pay_for_class}',
                r.remarks or '-'
            ])
        data.append(['', '', '', f'TOTAL: Rs.{total_salary}', ''])

        table = Table(data, colWidths=[1.2*inch, 2*inch, 1.5*inch, 1.2*inch, 1.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#344e80')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#cedce7'))
        ]))
        story.append(table)
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"<b>Total Classes Conducted:</b> {len(records)}", styles['Normal']))
        story.append(Paragraph(f"<b>Total Salary Earned:</b> Rs.{total_salary}", styles['Normal']))
    else:
        story.append(Paragraph("No attendance records found for this tutor.", styles['Normal']))

    story.append(Spacer(1, 20))
    story.append(Paragraph("Powered by Mentorscue — Online Tuition & Mentorship", footer_style))
    doc.build(story)
    buffer.seek(0)
    return buffer