# Media Conversion Tools

## Overview

The Media Conversion Tools application provides a user-friendly interface for converting videos to H.265 format and images to JPEG format, helping to save space on your hard drive. The application supports the following features:

### Video Conversion
- Scans specified folders and subfolders recursively.
- Converts all video files found from any format to the H.265 format using the MP4 container.
- Supports GPU encoding (NVIDIA and AMD) and CPU encoding.
- Allows the use of HandBrakeCLI or ffmpeg for video conversion.

### Image Conversion & Metadata Removal
- Scans specified folders and subfolders recursively.
- Converts all image files to the JPEG format.
- Adds a custom comment to the metadata of converted images to keep track of files already converted, allowing you to stop and resume the application as needed. After converting all image files you can use the Remove Metadata button to clear the comment off all files.
- Removes metadata from the "Description" section of the image files.

#### Files are sent to the recycling bin mainly for debugging purposes while creating this application to insure I didn't lose anything important. This part of the code could be changed to permenantly delete the files if you wish. Using the recylcing bin was the safest method while creating this application. If you decide to delete the files permenantly you can remove the Import send2trash library from the application altogether.

## Inspiration for creating this Application
After downloading a big OF collection, I used up too much space on my hard drive, so I needed a way to save space without deleting anything. By converting videos to H.265 and images to JPEG I reduced the space taken by almost one half. For example, a 500 MB video file can be reduced to around 200-250 MB. This application helped reduce over 1 TB of data to 558 GB, saving over 400 GB of storage space. H.265 has become extremely popular and is by far the best compressed video format that still holds extremely good details without losing much quality.

## Dependencies

### Included Dependencies
The following Windows binary dependencies are included in the `resources` folder:
- `ffmpeg` - version 7.1 Essentials (You can replace these with your own from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/))
- `ffprobe` - version 7.1 Essentials (You can replace these with your own from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/))
- `HandBrakeCLI` - version 1.9.0 (You can replace these with your own from [handbrake.fr](https://handbrake.fr/downloads2.php))

### Required Python Libraries
The application requires the following Python libraries:
- `PySide6`
- `send2trash`
- `Pillow`

### Installation
1. **Ensure you have Python 3.13.1 or later installed on your system.**
2. **Add Python to the PATH environment variables:**
   - **Windows:**
     1. Open the Start Search, type in "env", and select "Edit the system environment variables".
     2. In the System Properties window, click on the "Environment Variables" button.
     3. In the Environment Variables window, find the "Path" variable in the "System variables" section and select it. Click "Edit".
     4. Click "New" and add the path to your Python installation directory (e.g., `C:\Python39` or `C:\Users\YourUsername\AppData\Local\Programs\Python\Python39`).
     5. Click "OK" to close all windows.

3. **Install required libraries using `pip`:**
   ```bash
   pip install -r requirements.txt
   ```

### Note
If you are using the provided `MediaConversionTools.spec` file with PyInstaller, the `requirements.txt` file is not required. PyInstaller will bundle all necessary dependencies into the executable.

## Creating a Standalone Executable

To create a standalone executable using PyInstaller, follow these steps:

1. **Install PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Use the provided spec file to build the executable**:
   ```bash
   pyinstaller MediaConversionTools.spec
   ```

3. **After the build process is complete, you will find the standalone executable in the `dist` folder.**

## Usage

### Running the Application
1. **Execute the `main.py` script:**
   ```bash
   python main.py
   ```
2. **Alternatively, use the provided batch script to run the application:**
   ```batch
   @echo off
   python main.py
   pause
   ```
   - Create a shortcut of the batch file on your desktop for quick access.

### Customizing the Comment in Image Metadata
To change the comment added to the image metadata, modify the `COMMENT` variable at the top of the `utils.py` file:
```python
# Variable to store the comment added to image metadata
COMMENT = "ConvertedByFrostbyte"
```
Replace `ConvertedByFrostbyte` with your desired comment. For example:
```python
# Variable to store the comment added to image metadata
COMMENT = "YourCustomComment"
```

## Styling

The application supports the following styles on Windows 11:
- Fusion
- WindowsVista
- Windows

You can set the style in the `main.py` file:
```python
app.setStyle("Fusion")
```

### User Interface

#### Image Processing Tab
- **Directory Path:** Enter the directory path where the images are located.
- **Browse:** Browse to select the directory containing the images.
- **Use Max CPU Cores:** Enable this option to use the maximum number of CPU cores for processing.
- **Convert to JPG and Add Comment:** Convert all images in the directory to JPG format and add a comment to the metadata.
- **Remove All Metadata:** Remove all metadata from the images in the directory.
- **Stop All:** Stop all ongoing image processing operations.
- **Log Text Box:** Displays the log messages for image processing operations.
- **Total Photos:** Displays the total number of photos to be processed.
- **Remaining Photos:** Displays the number of photos remaining to be processed.
- **Status Bar:** Displays the current status of the image processing operations.
- **Progress Bar:** Displays the progress of the image processing operations.

#### Video Processing Tab
- **Directory Path:** Enter the directory path where the videos are located.
- **Browse:** Browse to select the directory containing the videos.
- **Enable GPU Encoding (Unchecked = CPU):** Enable this option to use NVIDIA GPU encoding for video processing. When unchecked, CPU encoding is used.
- **Enable AMD Encoding (Unchecked = NVIDIA):** Enable this option to use AMD instead of NVIDIA encoding for video processing. When unchecked, NVIDIA encoding is used.
- **Use HandBrake CLI (Unchecked = ffmpeg):** Enable this option to use HandBrake CLI instead of ffmpeg for video processing. When unchecked, ffmpeg is used.
- **Convert All Videos to h.265:** Start converting all videos in the directory to H.265 format.
- **Stop All:** Stop all ongoing video processing operations.
- **Log Text Box:** Displays the log messages for video processing operations.
- **ffmpeg Output Text Box:** Displays the output messages from ffmpeg during video processing.
- **Total Videos:** Displays the total number of videos to be processed.
- **Remaining Videos:** Displays the number of videos remaining to be processed.
- **Status Bar:** Displays the current status of the video processing operations.
- **Progress Bar:** Displays the progress of the video processing operations.

## Contributing

Contributions are welcome! Please feel free to fork this repository and submit pull requests.

## Disclaimer

**Disclaimer:** I am not responsible for any files deleted by this code. All video and image folders should be backed up before testing this application extensively. Ensure you have backups of your data before running the application on important folders. I have tested all parts of this application except the AMD GPU encoding as I do not own an AMD GPU to test it. All other parts have been tested extensively, including converting over 1,000 H.264, Quicktime, and AVI videos to H.265, as well as converting over 40,000 image files from BMP, JPG, JPEG, PNG, etc., to JPG. THIS APPLICATION WAS CREATED FOR WINDOWS PCs. IF YOU WANT TO USE IT ON LINUX SOME CHANGES WILL HAVE TO BE MADE. CODE CHANGES AND NECESSARY DEPENDENCIES WILL BE REQUIRED. I HAVE NO DESIRE TO MAKE A LINUX VERSION OF THIS BECAUSE I DON'T USE LINUX. IF SOMEONE WANTS TO FORK IT AND SET IT UP FOR LINUX THEY ARE WELCOME TO DO SO.

## License

This code is licensed under the [MIT License](LICENSE). The comment banner at the top of each file should remain intact if the code is reused or distributed. This code is not permitted for use in any commercial application without explicit permission.