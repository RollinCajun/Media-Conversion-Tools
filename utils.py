"""
Author: RollinCajun
Email: kastingwithfrostbyte@proton.me

Description:
This module contains utility functions for sanitizing paths, converting images,
removing metadata, and checking for ffprobe availability.
"""

import os
import shutil
from PIL import Image
import subprocess

# Variable to store the comment added to image metadata
COMMENT = "ConvertedByFrostbyte"

def sanitize_path(path):
    """
    Sanitize the given path by normalizing and converting it to an absolute path.
    """
    return os.path.normpath(os.path.abspath(path))

def convert_single_image(file_path):
    """
    Convert a single image to JPG format and add a comment to the metadata.
    If the image already has the comment, it will be skipped.
    """
    try:
        if file_path.lower().endswith(('.jpeg', '.png', '.gif', '.tiff', '.bmp', '.jpg')):
            # Check if the image already has the comment
            result = subprocess.run(['exiftool', '-XPComment', file_path], capture_output=True, text=True, check=True)
            if COMMENT in result.stdout:
                return f"Skipping {file_path}, comment found."
            # Open the image and convert it to JPG format
            with Image.open(file_path) as img:
                output_file = os.path.splitext(file_path)[0] + ".tmp"
                img.convert("RGB").save(output_file, "JPEG")
                print(f"Created tmp file: {output_file}")  # Debugging line
            # Add the comment to the metadata
            subprocess.run(['exiftool', '-overwrite_original', f'-XPComment={COMMENT}', output_file], check=True)
            return output_file
    except Exception as e:
        return f"Error processing {file_path}: {e}"
    return None

def remove_single_metadata(file_path):
    """
    Remove all metadata from a single image file.
    """
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
    """
    Check if ffprobe is available in the system's PATH.
    """
    return shutil.which("ffprobe") is not None