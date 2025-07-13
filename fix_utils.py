import re

# Step 1: Load your routes.py
with open("routes.py", "r", encoding="utf-8") as file:
    content = file.read()

# Step 2: Add `safe_parse_date` utility if it's not already there
if "def safe_parse_date" not in content:
    safe_parse = """
from datetime import datetime

def safe_parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None
"""
    content = safe_parse + content

# Step 3: Replace risky `datetime.strptime(...)` usages
content = re.sub(
    r"datetime\.strptime\((start_date|end_date),\s*'%Y-%m-%d'\)\.date\(\)",
    r"safe_parse_date(\1)", content)

# Step 4: Inject filter safety condition
# For student_profile
content = re.sub(
    r"elif start_date and end_date:\s*\n\s*attendance_query = attendance_query\.filter\(",
    "elif safe_parse_date(start_date) and safe_parse_date(end_date):\n        start = safe_parse_date(start_date)\n        end = safe_parse_date(end_date)\n        attendance_query = attendance_query.filter(",
    content)

# For tutor_profile
content = re.sub(
    r"elif start_date and end_date:\s*\n\s*attendance_query = attendance_query\.filter\(",
    "elif safe_parse_date(start_date) and safe_parse_date(end_date):\n        start = safe_parse_date(start_date)\n        end = safe_parse_date(end_date)\n        attendance_query = attendance_query.filter(",
    content)

# Step 5: Save the modified routes.py
with open("routes.py", "w", encoding="utf-8") as file:
    file.write(content)

print("✅ Patched routes.py with safe date filter handling.")
