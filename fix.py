# fix_add_tutor.py: Fixes the 'dob' -> 'date_of_birth' issue in add_tutor.html
import os

file_path = "templates/add_tutor.html"  # Update path if yours is different

if not os.path.exists(file_path):
    print(f"❌ File not found: {file_path}")
else:
    with open(file_path, "r") as f:
        content = f.read()

    # Apply necessary replacements
    content = content.replace('name="dob"', 'name="date_of_birth"')
    content = content.replace('id="dob"', 'id="date_of_birth"')
    content = content.replace('getElementById("dob")',
                              'getElementById("date_of_birth")')

    with open(file_path, "w") as f:
        f.write(content)

    print("✅ add_tutor.html patched successfully!")
