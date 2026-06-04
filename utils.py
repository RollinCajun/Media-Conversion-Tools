"""
Author: RollinCajun
Email: kastingwithfrostbyte@proton.me

Description:
This module contains utility functions for sanitizing paths, converting images,
removing metadata, and checking for ffprobe availability.
"""

import os
import shutil
from PIL import Image, JpegImagePlugin
import subprocess
import pillow_heif
from send2trash import send2trash

# Register HEIF format with Pillow
pillow_heif.register_heif_opener()

# Register JFIF format with Pillow
JpegImagePlugin._getmp = lambda: None

SUPPORTED_IMAGE_EXTENSIONS = (
    '.jpg', '.jpeg', '.jpe', '.jfif',
    '.png', '.gif', '.tiff', '.tif', '.bmp',
    '.heif', '.heic', '.webp', '.avif'
)

EXIFTOOL_PATH = shutil.which("exiftool")

# Variable to store the comment added to image metadata
COMMENT = "ConvertedByFrostbyte"


def is_supported_image_file(file_name):
    """Return True if the file has a supported image extension."""
    return os.path.splitext(file_name)[1].lower() in SUPPORTED_IMAGE_EXTENSIONS


def get_target_extension(format_name):
    """Return a normalized target extension for a format name."""
    normalized = format_name.strip().lower()
    if normalized == 'jpg':
        return '.jpg'
    if normalized == 'png':
        return '.png'
    return '.' + normalized.lstrip('.')


def get_save_format(format_name):
    """Return the Pillow save format string for a target format."""
    normalized = format_name.strip().lower()
    if normalized == 'jpg':
        return 'JPEG'
    if normalized == 'png':
        return 'PNG'
    return normalized.upper()


def is_exiftool_available():
    """Return True if exiftool is installed and available on the PATH."""
    return EXIFTOOL_PATH is not None

def sanitize_path(path):
    """
    Sanitize the given path by normalizing and converting it to an absolute path.
    """
    return os.path.normpath(os.path.abspath(path))

def convert_single_image(file_path, target_format='JPG'):
    """
    Convert a single image to the selected target format and safely replace the original.
    If the image already matches the target format, it will be skipped.
    """
    try:
        file_path = sanitize_path(file_path)  # Sanitize the file path
        print(f"Sanitized file path: {file_path}")  # Debugging line
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")  # Debugging line
            raise FileNotFoundError(f"The system cannot find the file specified: {file_path}")

        target_ext = get_target_extension(target_format)
        source_ext = os.path.splitext(file_path)[1].lower()
        output_file = os.path.splitext(file_path)[0] + target_ext

        if source_ext == target_ext:
            return f"Skipping {file_path}, already {target_format}."

        temp_output_file = output_file + ".tmp"
        save_format = get_save_format(target_format)
        success = False

        try:
            with Image.open(file_path) as img:
                img.convert("RGB").save(temp_output_file, save_format)
                print(f"Created temporary file: {temp_output_file}")  # Debugging line

            if not os.path.exists(temp_output_file):
                raise FileNotFoundError(f"Converted file was not created: {temp_output_file}")

            os.replace(temp_output_file, output_file)
            print(f"Renamed temporary file to final output: {output_file}")
            success = True

            if os.path.normcase(os.path.normpath(file_path)) != os.path.normcase(os.path.normpath(output_file)):
                send2trash(file_path)
                print(f"Sent original file to recycle bin: {file_path}")
            return output_file
        finally:
            if not success and os.path.exists(temp_output_file):
                try:
                    os.remove(temp_output_file)
                    print(f"Removed incomplete temporary file: {temp_output_file}")
                except Exception as cleanup_error:
                    print(f"Failed to remove incomplete temp file {temp_output_file}: {cleanup_error}")
    except FileNotFoundError as fnf_error:
        print(f"FileNotFoundError: {fnf_error}")  # Debugging line
        return f"Error processing {file_path}: {fnf_error}"
    except Exception as e:
        print(f"Error processing {file_path}: {e}")  # Debugging line
        return f"Error processing {file_path}: {e}"
    return None

def remove_single_metadata(file_path):
    """
    Remove all metadata from a single image file.
    """
    if not is_exiftool_available():
        return f"ExifTool is not available, cannot remove metadata from {file_path}."

    file_path = sanitize_path(file_path)
    temp_output_file = file_path + ".tmp"

    try:
        subprocess.run(
            [
                EXIFTOOL_PATH,
                '-o', temp_output_file,
                '-XPComment=',
                '-XPSubject=',
                '-XMP-dc:Subject=',
                '-XMP-dc:Title=',
                '-XMP-dc:Description=',
                '-XMP-microsoft:LastKeywordXMP=',
                '-Comment=',
                file_path
            ],
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        if not os.path.exists(temp_output_file):
            raise FileNotFoundError(f"Metadata-stripped file not created: {temp_output_file}")

        send2trash(file_path)
        os.replace(temp_output_file, file_path)
        return f"Removed metadata from {file_path}"
    except subprocess.CalledProcessError as e:
        if os.path.exists(temp_output_file):
            try:
                os.remove(temp_output_file)
            except Exception:
                pass
        return f"Error removing metadata from {file_path}: {e}"
    except Exception as e:
        if os.path.exists(temp_output_file):
            try:
                os.remove(temp_output_file)
            except Exception:
                pass
        return f"Error processing {file_path}: {e}"

def is_ffprobe_available():
    """
    Check if ffprobe is available in the system's PATH.
    """
    return shutil.which("ffprobe") is not None