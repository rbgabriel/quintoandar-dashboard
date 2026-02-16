path = "quintoandar_dashboard.py"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    # Adjust lines 201 to 216 (1-indexed in view_file were 201-216)
    # 0-indexed: 200 to 215
    if 200 <= i <= 215:
        if line.startswith("    "):
            new_lines.append(line[4:])
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

with open(path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)
print("Successfully fixed indentation in dashboard")
