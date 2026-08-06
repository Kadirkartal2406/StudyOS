from pathlib import Path

path = Path(r"C:\projects\StudyOS\backend\app\services\geography\turkey_catalog.py")
text = path.read_text(encoding="utf-8")
correct = "".join(map(chr, [82, 105, 122, 101]))  # Rize
idx = text.find('("rize", "')
if idx < 0:
    raise SystemExit("rize not found")
start = idx + len('("rize", "')
end = text.find('"', start)
old = text[start:end]
text = text[:start] + correct + text[end:]
path.write_text(text, encoding="utf-8")
print("old=", repr(old), "new=", repr(correct), "ords=", [ord(c) for c in correct])
