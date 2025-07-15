# fix_orphan_endfor.py

file_path = "templates/admin_dashboard.html"


def clean_orphan_endfor():
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()

        stack = []
        cleaned = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("{% for "):
                stack.append("for")
                cleaned.append(line)
            elif stripped.startswith("{% if"):
                stack.append("if")
                cleaned.append(line)
            elif stripped.startswith("{% else %}") or stripped.startswith(
                    "{% elif"):
                cleaned.append(line)
            elif stripped.startswith("{% endfor %}"):
                if "for" in stack:
                    stack.remove("for")
                    cleaned.append(line)
                else:
                    print(f"ðŸ§¹ Removed orphan endfor at line {i+1}")
            elif stripped.startswith("{% endif %}"):
                if "if" in stack:
                    stack.remove("if")
                    cleaned.append(line)
                else:
                    print(f"ðŸ§¹ Removed orphan endif at line {i+1}")
            else:
                cleaned.append(line)

        with open(file_path, "w") as f:
            f.writelines(cleaned)

        print("âœ… Orphan {% endfor %} and {% endif %} cleanup completed.")

    except Exception as e:
        print(f"âŒ Error: {e}")


if __name__ == "__main__":
    clean_orphan_endfor()
