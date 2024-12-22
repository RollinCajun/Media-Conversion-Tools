import os
import shutil
from PIL import Image
import subprocess

def sanitize_path(path):
    return os.path.normpath(os.path.abspath(path))

def convert_single_image(file_path):
    try:
        if file_path.lower().endswith(('.jpeg', '.png', '.gif', '.tiff', '.bmp', '.jpg')):
            result = subprocess.run(['exiftool', '-XPComment', file_path], capture_output=True, text=True, check=True)
            if "ConvertedByFrostbyte" in result.stdout:
                return f"Skipping {file_path}, comment found."
            with Image.open(file_path) as img:
                output_file = os.path.splitext(file_path)[0] + ".tmp"
                img.convert("RGB").save(output_file, "JPEG")
                print(f"Created tmp file: {output_file}")  # Debugging line
            subprocess.run(['exiftool', '-overwrite_original', '-XPComment=ConvertedByFrostbyte', output_file], check=True)
            return output_file
    except Exception as e:
        return f"Error processing {file_path}: {e}"
    return None

def remove_single_metadata(file_path):
    try:
        subprocess.run(
            ['exiftool', '-overwrite_original', '-XPComment=', '-XPSubject=', '-XMP-dc:Subject=', '-XMP-dc:Title=', '-XMP-dc:Description=', '-XMP-microsoft:LastKeywordXMP=', '-Comment=', file_path],
            check=True
        )
        return f"Removed metadata from {file_path}"
    except subprocess.CalledProcessError as e:
        return f"Error removing metadata from {file_path}: {e}"
    except Exception as e:
        return f"Error processing {file_path}: {e}"

def is_ffprobe_available():
    """Check if ffprobe is available in the system's PATH."""
    return shutil.which("ffprobe") is not None