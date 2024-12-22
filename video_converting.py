import os
import subprocess
from send2trash import send2trash
from datetime import datetime
from PySide6.QtCore import QThread, Signal
from utils import sanitize_path, is_ffprobe_available

class VideoWorkerThread(QThread):
    update_status = Signal(str)
    update_status_bar = Signal(str)
    update_ffmpeg_output = Signal(str)
    update_progress = Signal(int)
    update_remaining_videos = Signal(int)
    finished = Signal()

    def __init__(self, directory, use_gpu):
        super().__init__()
        self.directory = sanitize_path(directory)
        self.use_gpu = use_gpu
        self.stop_event = False
        self.error_log_file = sanitize_path(os.path.join(directory, "error_log.txt"))

        # Check if ffprobe is available
        if not is_ffprobe_available():
            raise EnvironmentError("ffprobe is not available in the system's PATH.")

    def run(self):
        self.clean_temp_files(self.directory)
        self.process_videos(self.directory, self.use_gpu)
        self.finished.emit()

    def stop(self):
        self.stop_event = True

    def clean_temp_files(self, directory):
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".h265.mp4"):
                    send2trash(sanitize_path(os.path.join(root, file)))
                    self.update_status_bar.emit(f"Moved leftover file to recycle bin: {file}")

    def process_videos(self, directory, use_gpu):
        files_to_process = [sanitize_path(os.path.join(root, file)) for root, _, files in os.walk(directory) for file in files if self.is_video_file(file)]
        total_files = len(files_to_process)

        for i, file_path in enumerate(files_to_process):
            if self.stop_event:
                break
            self.update_status_bar.emit(f"Processing {file_path}")

            if not self.is_h265(file_path):
                self.update_status_bar.emit(f"Converting {file_path} to H.265...")
                try:
                    self.convert_to_h265(file_path, use_gpu)
                    self.rename_and_cleanup(file_path)
                    self.update_status.emit(f"{file_path} converted to H.265!")
                except Exception as e:
                    self.log_error(file_path, e)
                    self.update_status.emit(f"Error converting {file_path}: {e}")
            else:
                self.update_status_bar.emit(f"Skipping {file_path}, already H.265")

            self.update_ffmpeg_output.emit(f"Progress: {i + 1}/{total_files}")
            self.update_progress.emit(int((i + 1) / total_files * 100))
            self.update_remaining_videos.emit(total_files - (i + 1))

        self.update_status_bar.emit("Video processing completed.")

    def is_video_file(self, file):
        return file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))

    def is_h265(self, file_path):
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_name', '-of', 'default=nw=1:nk=1', file_path],
                capture_output=True, text=True, check=True
            )
            return 'hevc' in result.stdout
        except FileNotFoundError as e:
            self.log_error(file_path, e)
            self.log_error(file_path, f"Environment PATH: {os.environ['PATH']}")
            raise e
        except subprocess.CalledProcessError as e:
            self.log_error(file_path, e)
            raise e

    def convert_to_h265(self, file_path, use_gpu):
        output_file = sanitize_path(os.path.splitext(file_path)[0] + ".h265.mp4")
        if use_gpu:
            command = ['ffmpeg', '-i', file_path, '-c:v', 'hevc_nvenc', '-c:a', 'copy', '-map_metadata', '-1', '-sn', '-y', output_file]
        else:
            command = ['ffmpeg', '-i', file_path, '-c:v', 'libx265', '-c:a', 'copy', '-map_metadata', '-1', '-sn', '-y', output_file]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')
        while True:
            if self.stop_event:
                process.terminate()
                break
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self.update_ffmpeg_output.emit(output.strip())

    def rename_and_cleanup(self, file_path):
        old_file = sanitize_path(file_path)
        new_file = sanitize_path(os.path.splitext(file_path)[0] + ".h265.mp4")
        final_file = sanitize_path(os.path.splitext(file_path)[0] + ".mp4")

        if os.path.exists(new_file):
            send2trash(old_file)
            os.rename(new_file, final_file)

    def log_error(self, file_path, error):
        with open(self.error_log_file, 'a', encoding='utf-8') as log_file:
            log_file.write(f"{datetime.now()}: Error processing {file_path} - {error}\n")
            if isinstance(error, subprocess.CalledProcessError):
                log_file.write(f"Command: {error.cmd}\n")
                log_file.write(f"Return Code: {error.returncode}\n")
                log_file.write(f"Output: {error.output}\n")