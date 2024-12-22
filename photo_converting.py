"""
Author: RollinCajun
Email: kastingwithfrostbyte@proton.me

Description:
This module handles image processing tasks such as converting images to JPG and removing metadata.
"""

import os
import time
import concurrent.futures
from PIL import Image
from send2trash import send2trash
from PySide6.QtCore import QThread, Signal
from utils import sanitize_path, convert_single_image, remove_single_metadata

class ImageWorkerThread(QThread):
    # Signals to update the UI
    update_status = Signal(str)
    update_status_bar = Signal(str)
    update_progress = Signal(int)
    update_remaining_photos = Signal(int)
    finished = Signal()

    def __init__(self, directory, use_max_cores, task):
        super().__init__()
        self.directory = sanitize_path(directory)  # Sanitize the directory path
        self.use_max_cores = use_max_cores  # Flag to use maximum CPU cores
        self.task = task  # Task to perform: 'convert' or 'remove_metadata'
        self.stop_event = False  # Flag to stop the thread

    def run(self):
        # Determine the task to perform
        if self.task == 'convert':
            self.convert_to_jpg(self.directory, self.use_max_cores)
        elif self.task == 'remove_metadata':
            self.remove_metadata(self.directory, self.use_max_cores)
        self.finished.emit()  # Emit finished signal when done

    def stop(self):
        self.stop_event = True  # Set stop event flag to True

    def convert_to_jpg(self, directory, use_max_cores):
        start_time = time.time()  # Record start time
        # Collect all image files in the directory and subdirectories
        files_to_process = [os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if file.lower().endswith(('.jpeg', '.png', '.gif', '.tiff', '.bmp', '.jpg'))]
        total_files = len(files_to_process)  # Total number of files to process
        max_workers = os.cpu_count() if use_max_cores else 2  # Determine number of workers

        # Use a ThreadPoolExecutor to process files concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(convert_single_image, file_path): file_path for file_path in files_to_process}
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                if self.stop_event:
                    break  # Stop processing if stop event is set
                try:
                    result = future.result()  # Get the result of the future
                    if "Skipping" in result:
                        self.update_status_bar.emit(result)  # Update status bar if skipping
                    else:
                        original_file = futures[future]  # Get the original file path
                        new_file = result  # Get the new file path
                        if os.path.exists(new_file):
                            send2trash(original_file)  # Move original file to recycle bin
                            final_file = os.path.splitext(original_file)[0] + ".jpg"  # Determine final file path
                            os.rename(new_file, final_file)  # Rename new file to final file
                            self.update_status.emit(f"Completed: {final_file}")  # Update status
                        else:
                            self.update_status_bar.emit(f"Error: New file does not exist for {original_file}")
                    self.update_progress.emit(int((i + 1) / total_files * 100))  # Update progress bar
                    self.update_remaining_photos.emit(total_files - (i + 1))  # Update remaining photos count
                except Exception as exc:
                    self.update_status_bar.emit(f"Error: {exc}")  # Update status bar with error

        end_time = time.time()  # Record end time
        elapsed_time = end_time - start_time  # Calculate elapsed time
        summary = (
            "------------------------------------------\n"
            "Conversion Results:\n\n"
            f"Total Files: {total_files}\n"
            f"Completed in {elapsed_time:.2f} seconds!\n"
            "------------------------------------------\n"
        )
        self.update_status.emit(summary)  # Update status with summary

    def remove_metadata(self, directory, use_max_cores):
        # Collect all JPG files in the directory and subdirectories
        files_to_process = [os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if file.lower().endswith('.jpg')]
        total_files = len(files_to_process)  # Total number of files to process
        max_workers = os.cpu_count() if use_max_cores else 2  # Determine number of workers

        # Use a ThreadPoolExecutor to process files concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(remove_single_metadata, file_path): file_path for file_path in files_to_process}
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                if self.stop_event:
                    break  # Stop processing if stop event is set
                try:
                    result = future.result()  # Get the result of the future
                    if "Skipping" in result:
                        self.update_status_bar.emit(result)  # Update status bar if skipping
                    else:
                        self.update_status.emit(f"Completed: {result}")  # Update status
                    self.update_progress.emit(int((i + 1) / total_files * 100))  # Update progress bar
                    self.update_remaining_photos.emit(total_files - (i + 1))  # Update remaining photos count
                except Exception as exc:
                    self.update_status.emit(f"Generated an exception: {exc}")  # Update status with error

        self.update_status.emit("Metadata removal completed.")  # Update status when done