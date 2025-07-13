# MentorsCue Deployment Guide

## Production-Ready Changes Made

### 1. Application Structure
- ✅ Created `requirements_render.txt` with all dependencies including gunicorn
- ✅ Configured app to run with `gunicorn app:app` 
- ✅ Removed debug flags and app.run() calls for production
- ✅ Proper SQLite database path using `os.path.join` with `__file__`
- ✅ Added environment-based logging (INFO for production)

### 2. Admin Authentication Added
- ✅ Added Admin model with secure password hashing
- ✅ Created admin login system with session management
- ✅ Protected all admin routes with `@admin_required` decorator
- ✅ Default admin user: username='admin', password='admin123'

### 3. Deployment Files Created
- ✅ `Procfile` for Heroku-style deployments
- ✅ `render.yaml` for Render deployment with PostgreSQL
- ✅ `requirements_render.txt` for dependency management

### 4. Folder Structure Verified
```
mentorscue/
├── app.py                 # Main Flask application
├── main.py                # Entry point (for gunicorn)
├── models.py              # Database models
├── routes.py              # Application routes
├── utils.py               # PDF generation utilities
├── requirements_render.txt # Dependencies for deployment
├── Procfile               # Process file for deployment
├── render.yaml            # Render configuration
├── templates/             # Jinja2 templates
│   ├── base.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   ├── tutor_login.html
│   ├── tutor_submit.html
│   ├── add_student.html
│   ├── edit_student.html
│   ├── add_tutor.html
│   ├── edit_tutor.html
│   └── view_attendance.html
└── static/                # Static assets
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## Render Deployment Steps

### Option 1: Using render.yaml (Recommended)
1. Push code to GitHub repository
2. Connect Render to your GitHub repo
3. Render will automatically detect `render.yaml` configuration
4. Environment variables will be set up automatically

### Option 2: Manual Setup
1. Create new Web Service on Render
2. Set build command: `pip install -r requirements_render.txt`
3. Set start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
4. Set environment variables:
   - `FLASK_ENV=production`
   - `SESSION_SECRET=your-secret-key`
   - `DATABASE_URL=postgresql://...` (from Render PostgreSQL)

### Option 3: Copy requirements_render.txt to requirements.txt
If Render expects `requirements.txt`, copy the content:
```bash
cp requirements_render.txt requirements.txt
```

## Environment Variables Required

### Required for Production:
- `SESSION_SECRET`: Strong secret key for sessions
- `DATABASE_URL`: PostgreSQL connection string (provided by Render)
- `FLASK_ENV`: Set to 'production'

### Optional:
- `PORT`: Will be provided by Render automatically

## Default Admin Access
- **Username:** admin
- **Password:** admin123
- **⚠️ IMPORTANT:** Change the default password immediately after first login

## Features Available After Deployment

### Admin Dashboard (Login Required):
- Student management (CRUD operations)
- Tutor management with secure credentials
- Attendance record viewing and management
- PDF invoice generation for parents and tutors
- Bulk operations for attendance records

### Tutor Portal:
- Secure login with username/password
- Attendance submission for assigned students
- Subject and date tracking with optional remarks

### PDF Invoices:
- Parent invoices: Subject-wise breakdown with total fees
- Tutor invoices: Class details with salary calculation
- Professional branding with MentorsCue footer

## Database Migration

The app will automatically:
1. Create all database tables on first run
2. Set up the default admin user
3. Handle PostgreSQL connection via DATABASE_URL

## Security Features

✅ Password hashing with Werkzeug security
✅ Session-based authentication
✅ Admin route protection
✅ Environment-based configuration
✅ Production-ready logging
✅ CSRF protection via Flask sessions

## Testing Before Deployment

1. Test admin login at `/admin_login`
2. Test tutor login at `/tutor_login`  
3. Verify all CRUD operations work
4. Test PDF generation functionality
5. Check responsive design on mobile

## Support

For deployment issues:
1. Check Render logs for detailed error messages
2. Verify all environment variables are set
3. Ensure PostgreSQL database is connected
4. Check that all dependencies are in requirements_render.txt