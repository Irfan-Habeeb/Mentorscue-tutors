import re

file_path = 'utils.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace incorrect currency symbol
content = content.replace('â‚¹', '₹')

# 2. Replace <b>₹ amounts</b> with Paragraphs (prepare Paragraph version replacements)
# We'll use a very simple rule to detect and replace it safely
content = re.sub(
    r"'<b>Total:</b>',\s*f'<b>₹\{.*?\}</b>'",
    "Paragraph('Total:', bold_style), Paragraph(f'₹{total_amount}', bold_style)",
    content
)

content = re.sub(
    r"f'<b>Total: ₹\{.*?\}</b>'",
    "Paragraph(f'Total: ₹{total_salary}', bold_style)",
    content
)

# 3. Remove duplicated datetime imports inside blocks
content = re.sub(r'(\n\s*)from datetime import datetime', '', content)

# 4. Ensure try/except around doc.build
if "try:\n    doc.build(story)" not in content:
    content = content.replace(
        "doc.build(story)",
        "try:\n    doc.build(story)\nexcept Exception as e:\n    logger.error(f\"PDF Build Error: {e}\")\n    raise"
    )

# 5. Add bold_style if not present
if "bold_style" not in content:
    insert_point = content.find("styles = getSampleStyleSheet()")
    new_style = """
bold_style = ParagraphStyle(
    name='Bold',
    parent=styles['Normal'],
    fontName='Helvetica-Bold'
)
"""
    content = content[:insert_point] + new_style + content[insert_point:]

# Save changes back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ utils.py has been updated successfully with all fixes.")