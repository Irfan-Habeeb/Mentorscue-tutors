import os

def replace_in_file(file_path, replacements):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    with open(file_path, 'r') as f:
        content = f.read()
    for old, new in replacements.items():
        content = content.replace(old, new)
    with open(file_path, 'w') as f:
        f.write(content)
    print(f"✅ Fixed: {file_path}")

replacements = {
    "url_for('generate_parent_invoice'": "url_for('handle_generate_parent_invoice'",
    "url_for('generate_tutor_invoice'": "url_for('handle_generate_tutor_invoice'"
}

# Edit these if needed
files_to_fix = [
    "routes.py",
    "templates/admin_dashboard.html",
    "templates/student_profile.html",
    "templates/tutor_profile.html"
]

for file in files_to_fix:
    replace_in_file(file, replacements)