from pathlib import Path
import re

path = Path(r"C:\projects\StudyOS\backend\app\services\geography\turkey_catalog.py")
text = path.read_text(encoding="utf-8")
m = re.search(r'\("rize", "([^"]+)",', text)
print("rize name:", repr(m.group(1)) if m else None)

# Force correct name and remove broken fixer
text2 = re.sub(r'\("rize", "[^"]+",', '("rize", "Rize",', text)
# Wait - write Rize correctly using chr codes: R i z e
correct = "R" + "ize"
text2 = re.sub(r'\("rize", "[^"]+",', f'("rize", "{correct}",', text)

# Remove _fix_rize_name block
text2 = re.sub(
    r"\ndef _fix_rize_name\(\) -> None:.*?_fix_rize_name\(\)\n\n",
    "\n",
    text2,
    flags=re.S,
)
path.write_text(text2, encoding="utf-8")
m2 = re.search(r'\("rize", "([^"]+)",', text2)
print("fixed:", repr(m2.group(1)) if m2 else None)
print("fixer gone:", "_fix_rize_name" not in text2)
