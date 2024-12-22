import os
import time
import concurrent.futures
from PIL import Image
from send2trash import send2trash
from PySide6.QtCore import QThread, Signal
from utils import sanitize_path, convert_single_image, remove_single_metadata

class ImageWorkerThread(QThread):
    update_status = Signal(str)
    update_status_bar = Signal(str)
    update_progress = Signal(int)
    update_remaining_photos = Signal(int)
    finished = Signal()

    def __init__(self, directory, use_max_cores, task):
        super().__init__()
        self.directory = sanitize_path(directory)
        self.use_max_cores = use_max_cores
        self.task = task
        self.stop_event = False

    def run(self):
        if self.task == 'convert':
            self.convert_to_jpg(self.directory, self.use_max_cores)
        elif self.task == 'remove_metadata':
            self.remove_metadata(self.directory, self.use_max_cores)
        self.finished.emit()

    def stop(self):
        self.stop_event = True

    def convert_to_jpg(self, directory, use_max_cores):
        start_time = time.time()
        files_to_process = [os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if file.lower().endswith(('.jpeg', '.png', '.gif', '.tiff', '.bmp', '.jpg'))]
        total_files = len(files_to_process)
        max_workers = os.cpu_count() if use_max_cores else 2

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(convert_single_image, file_path): file_path for file_path in files_to_process}
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                if self.stop_event:
                    break
                try:
                    result = future.result()
                    if "Skipping" in result:
                        self.update_status_bar.emit(result)
                    else:
                        original_file = futures[future]
                        new_file = result
                        if os.path.exists(new_file):
                            send2trash(original_file)
                            final_file = os.path.splitext(original_file)[0] + ".jpg"
                            os.rename(new_file, final_file)
                            self.update_status.emit(f"Completed: {final_file}")
                        else:
                            self.update_status_bar.emit(f"Error: New file does not exist for {original_file}")
                    self.update_progress.emit(int((i + 1) / total_files * 100))
                    self.update_remaining_photos.emit(total_files - (i + 1))
                except Exception as exc:
                    self.update_status_bar.emit(f"Error: {exc}")

        end_time = time.time()
        elapsed_time = end_time - start_time
        summary = (
            "------------------------------------------\n"
            "Conversion Results:\n\n"
            f"Total Files: {total_files}\n"
            f"Completed in {elapsed_time:.2f} seconds!\n"
            "------------------------------------------\n"
        )
        self.update_status.emit(summary)

    def remove_metadata(self, directory, use_max_cores):
        files_to_process = [os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if file.lower().endswith('.jpg')]
        total_files = len(files_to_process)
        max_workers = os.cpu_count() if use_max_cores else 2

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(remove_single_metadata, file_path): file_path for file_path in files_to_process}
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                if self.stop_event:
                    break
                try:
                    result = future.result()
                    if "Skipping" in result:
                        self.update_status_bar.emit(result)
                    else:
                        self.update_status.emit(f"Completed: {result}")
                    self.update_progress.emit(int((i + 1) / total_files * 100))
                    self.update_remaining_photos.emit(total_files - (i + 1))
                except Exception as exc:
                    self.update_status.emit(f"Generated an exception: {exc}")

        self.update_status.emit("Metadata removal completed.")