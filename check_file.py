import os
from pathlib import Path

BASE_DIR = Path(os.getcwd())
MEDIA_ROOT = BASE_DIR / 'media'
file_path = MEDIA_ROOT / 'company_logos' / '20f858b8-6f25-4880-9680-45223701a17e.jpg'

print(f"Checking file: {file_path}")
if file_path.exists():
    print("File exists.")
    print(f"Size: {file_path.stat().st_size} bytes")
else:
    print("File does NOT exist.")
