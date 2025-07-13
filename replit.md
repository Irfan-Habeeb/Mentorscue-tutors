# MentorsCue - Tuition Management System

## Overview

MentorsCue is a full-stack Flask web application designed for managing tuition classes and student-tutor interactions. The system provides role-based access with an admin dashboard for management tasks and a secure tutor portal for attendance tracking. The application focuses on simplicity and efficiency in managing students, tutors, attendance records, and generating invoices.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 with Flask for server-side rendering
- **UI Framework**: Bootstrap 5 for responsive design and components
- **Styling**: Custom CSS with Google Fonts (Cormorant Garamond for headings, Figtree for body text)
- **JavaScript**: Vanilla JavaScript for form validation and interactive elements
- **Color Scheme**: Background (#cedce7), Primary (#344e80), Accent (#43a24c), Text (#2e3a4d)

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database ORM**: SQLAlchemy with Flask-SQLAlchemy extension
- **Authentication**: Session-based authentication using Flask sessions
- **Password Security**: Werkzeug's security utilities for password hashing
- **PDF Generation**: ReportLab for creating downloadable invoices

### Database Design
- **Type**: SQLite for development (configured to support PostgreSQL via environment variables)
- **ORM**: SQLAlchemy with declarative base model
- **Connection Management**: Connection pooling with automatic reconnection

## Key Components

### Data Models
1. **Student Model**
   - Basic information (name, class level)
   - Fee structure (₹160/180/200 per class)
   - Tutor assignment and subjects
   - Relationship with attendance records

2. **Tutor Model**
   - Personal information and class groups they teach
   - Pay structure (₹100/120/140 per class)
   - Secure login credentials with hashed passwords
   - Relationship with assigned students and attendance

3. **Attendance Model**
   - Links tutors and students for specific sessions
   - Subject and date tracking
   - Optional remarks for each session

### Authentication System
- **Admin Access**: No authentication required for admin dashboard
- **Tutor Access**: Username/password authentication with session management
- **Password Security**: Bcrypt hashing via Werkzeug security utilities
- **Session Management**: Flask sessions for maintaining tutor login state

### Invoice Generation
- **Parent Invoices**: Subject-wise breakdown with total fees calculation
- **Tutor Invoices**: Class count, student details, and salary calculation
- **PDF Format**: Professional layout with ReportLab library
- **Branding**: Includes MentorsCue logo and footer

## Data Flow

### Admin Workflow
1. Admin accesses dashboard without authentication
2. Can perform CRUD operations on students and tutors
3. Views all attendance records across tutors
4. Generates and downloads PDF invoices
5. Manages tutor credentials and assignments

### Tutor Workflow
1. Tutor logs in with username/password
2. Redirected to attendance submission form
3. Selects from assigned students only
4. Submits attendance with subject and optional remarks
5. Data stored with tutor ID for tracking

### Data Processing
- Form submissions validated on both client and server side
- Database operations wrapped in try-catch for error handling
- Automatic timestamp generation for all records
- Relationship integrity maintained through foreign keys

## External Dependencies

### Python Packages
- **Flask**: Core web framework
- **Flask-SQLAlchemy**: Database ORM integration
- **Werkzeug**: Security utilities and WSGI support
- **ReportLab**: PDF generation for invoices

### Frontend Libraries
- **Bootstrap 5**: CSS framework for responsive design
- **Font Awesome**: Icon library for UI elements
- **Google Fonts**: Typography (Cormorant Garamond, Figtree)

### Database
- **SQLite**: Default for development and small deployments
- **PostgreSQL**: Configurable via DATABASE_URL environment variable
- **Connection Pooling**: Configured for production stability

## Deployment Strategy

### Environment Configuration
- **Development**: SQLite database with debug mode enabled
- **Production**: Environment variables for database URL and secret keys
- **Security**: Session secrets configurable via environment variables

### File Structure
- **Static Assets**: CSS and JavaScript in `/static` directory
- **Templates**: Jinja2 templates in `/templates` directory with base template inheritance
- **Database**: SQLite file in project root (for development)
- **Application**: Modular structure with separate files for routes, models, and utilities

### Scalability Considerations
- Database connection pooling configured for concurrent users
- Modular code structure allows for easy feature additions
- Template inheritance reduces code duplication
- Environment-based configuration supports different deployment scenarios

### Performance Features
- **Database Optimization**: Pre-ping and connection recycling configured
- **Frontend Optimization**: Bootstrap CDN for faster loading
- **Session Management**: Efficient session handling for tutor authentication
- **PDF Generation**: In-memory buffer for invoice generation to avoid file system overhead