# detect_jfif.py
import sys, os, imghdr
from PIL import Image

if len(sys.argv) < 2:
    print("Usage: python detect_jfif.py <folder-path>")
    sys.exit(1)

directory = sys.argv[1]
exts = ('.jpeg', '.png', '.gif', '.tiff', '.bmp', '.jpg', '.heic', '.jfif', '.webp')

ext_matches = []
other_files = []

for root, _, files in os.walk(directory):
    for f in files:
        full = os.path.join(root, f)
        if f.lower().endswith(exts):
            ext_matches.append(full)
        else:
            other_files.append(full)

print("Directory:", directory)
print("Total files found (walk):", sum(1 for _ in (os.walk(directory) and (_ for _ in [])) ) or 'see counts below')  # placeholder, we'll show lists
print()
print("Matches by extension:", len(ext_matches))
for p in ext_matches:
    try:
        size = os.path.getsize(p)
    except Exception as e:
        size = f"error getting size: {e}"
    try:
        fmt = imghdr.what(p)
    except Exception as e:
        fmt = f"imghdr error: {e}"
    try:
        with Image.open(p) as im:
            pil_fmt = im.format
            mode = im.mode
            ok = True
    except Exception as e:
        pil_fmt = f"open error: {e}"
        mode = ""
        ok = False
    print(f"- {p} | {size} bytes | imghdr={fmt} | Pillow format={pil_fmt} | open_ok={ok} | mode={mode}")

print()
print("Other files scanned (non-extension matches) [first 200]:", len(other_files))
for p in other_files[:200]:
    try:
        size = os.path.getsize(p)
    except Exception as e:
        size = f"error getting size: {e}"
    try:
        fmt = imghdr.what(p)
    except Exception as e:
        fmt = f"imghdr error: {e}"
    try:
        with Image.open(p) as im:
            pil_fmt = im.format
            mode = im.mode
            ok = True
    except Exception as e:
        pil_fmt = f"open error: {e}"
        mode = ""
        ok = False
    print(f"- {p} | {size} bytes | imghdr={fmt} | Pillow format={pil_fmt} | open_ok={ok} | mode={mode}")