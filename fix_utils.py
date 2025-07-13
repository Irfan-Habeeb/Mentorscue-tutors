import os

file_path = "utils.py"

if not os.path.exists(file_path):
    print("utils.py not found.")
    exit()

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace malformed or unsupported rupee symbols
replacements = {
    "â‚¹": "Rs.",
    "₹": "Rs.",
    "f'₹": "f'Rs. ",
    'f"₹': 'f"Rs. ',
    "<b>₹": "<b>Rs. ",
    "</b>₹": "</b>Rs. ",
    "₹</b>": "Rs.</b>",
}

for old, new in replacements.items():
    content = content.replace(old, new)

# Optional: add print to confirm replacements
print("✅ Replaced all rupee symbols with 'Rs.'")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ utils.py updated successfully!")