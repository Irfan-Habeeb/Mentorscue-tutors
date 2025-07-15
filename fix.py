# fix_button_spacing.py

file_path = "templates/admin_dashboard.html"


def patch_buttons():
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()

        patched_lines = []
        for line in lines:
            if 'class="btn ' in line and 'w-100' in line and 'mb-3' not in line:
                line = line.replace('w-100', 'w-100 mb-3')
            patched_lines.append(line)

        with open(file_path, "w") as f:
            f.writelines(patched_lines)

        print("âœ… Button spacing patched with 'mb-3' successfully.")

    except Exception as e:
        print(f"âŒ Error patching file: {e}")


if __name__ == "__main__":
    patch_buttons()
