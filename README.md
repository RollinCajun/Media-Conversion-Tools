# Media Conversion Tools

This Python application provides tools for:

1. **Video Conversion:** 
    - Scans specified folders and subfolders recursively.
    - Converts all video files found to the H.265 format using the MP4 container.

2. **Image Conversion & Metadata Removal:**
    - Scans specified folders and subfolders recursively.
    - Converts all image files to the JPEG format.
    - Removes metadata from the "Description" section of the image files.

**Usage:**

1. **Installation:**
   - **Requirements:** Ensure you have Python installed on your system.
   - Install required libraries using `pip`:
     ```bash
     pip install -r requirements.txt 
     ```

2. **Run the Application:**
   - Execute the `main.py` script.
   - The application will prompt you for the source folder path.
   - The application will then process the files and display progress updates.

**Note:**

* This is a basic implementation and may require further enhancements.
* Consider adding features like:
    - Command-line arguments for input/output paths.
    - Logging for better debugging.
    - User-friendly progress bar.
    - More robust error handling.

**Contributing:**

Contributions are welcome! Please feel free to fork this repository and submit pull requests.

**License:**

[Choose a suitable license, e.g., MIT License]

---

**Disclaimer:**

This is a basic template. You can customize it further to include:

* More detailed instructions.
* Screenshots or GIFs demonstrating the application.
* Architecture diagrams (if applicable).
* A list of known issues or limitations.
* Information about the development environment.

This `README.md` file provides a starting point for documenting your project on GitHub. Remember to update it as you develop and improve your application.