import os
import subprocess
from send2trash import send2trash
from datetime import datetime
from PySide6.QtCore import QThread, Signal
from utils import sanitize_path

class VideoWorkerThread(QThread):
    # Signals to update the UI
    update_status = Signal(str)
    update_status_bar = Signal(str)
    update_ffmpeg_output = Signal(str)
    update_progress = Signal(int)
    update_remaining_videos = Signal(int)
    finished = Signal()

    def __init__(self, directory, use_gpu, use_handbrake, use_amd):
        super().__init__()
        self.directory = sanitize_path(directory)  # Sanitize the directory path
        self.use_gpu = use_gpu  # Flag to use GPU for processing
        self.use_handbrake = use_handbrake  # Flag to use HandBrakeCLI
        self.use_amd = use_amd  # Flag to use AMD encoding
        self.stop_event = False  # Flag to stop the thread
        self.error_log_file = sanitize_path(os.path.join(directory, "error_log.txt"))  # Path to the error log file

        # Path to ffprobe in the resources folder
        self.ffprobe_path = sanitize_path(os.path.join(os.path.dirname(__file__), "resources", "ffprobe.exe"))
        # Path to ffmpeg in the resources folder
        self.ffmpeg_path = sanitize_path(os.path.join(os.path.dirname(__file__), "resources", "ffmpeg.exe"))

    def run(self):
        self.clean_temp_files(self.directory)  # Clean up any leftover temporary files
        self.process_videos(self.directory, self.use_gpu, self.use_handbrake, self.use_amd)  # Process the videos
        self.finished.emit()  # Emit finished signal when done

    def stop(self):
        self.stop_event = True  # Set stop event flag to True

    def clean_temp_files(self, directory):
        """
        Clean up any leftover temporary files in the directory.
        """
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".h265.mp4"):
                    send2trash(sanitize_path(os.path.join(root, file)))
                    self.update_status_bar.emit(f"Moved leftover file to recycle bin: {file}")

    def process_videos(self, directory, use_gpu, use_handbrake, use_amd):
        """
        Process all video files in the directory and subdirectories.
        """
        files_to_process = [sanitize_path(os.path.join(root, file)) for root, _, files in os.walk(directory) for file in files if self.is_video_file(file)]
        total_files = len(files_to_process)  # Total number of files to process

        for i, file_path in enumerate(files_to_process):
            if self.stop_event:
                break  # Stop processing if stop event is set

            if not self.is_h265(file_path):
                self.update_status_bar.emit(f"Processing {file_path}")
                self.update_status_bar.emit(f"Converting {file_path} to H.265...")
                try:
                    if use_handbrake:
                        self.convert_to_h265_handbrake(file_path, use_gpu, use_amd)  # Convert the video to H.265 using HandBrakeCLI
                    else:
                        self.convert_to_h265_ffmpeg(file_path, use_gpu, use_amd)  # Convert the video to H.265 using ffmpeg
                    self.rename_and_cleanup(file_path)  # Rename and clean up the files
                    self.update_status.emit(f"{file_path} converted to H.265!")
                except Exception as e:
                    self.log_error(file_path, e)  # Log any errors
                    self.update_status.emit(f"Error converting {file_path}: {e}")
            else:
                if not file_path.lower().endswith('.mp4'):
                    final_file = sanitize_path(os.path.splitext(file_path)[0] + ".mp4")
                    os.rename(file_path, final_file)
                    self.update_status.emit(f"Renamed {file_path} to {final_file}")
                self.update_status_bar.emit(f"Skipping {file_path}, already H.265")

            self.update_ffmpeg_output.emit(f"Progress: {i + 1}/{total_files}")  # Update ffmpeg output
            self.update_progress.emit(int((i + 1) / total_files * 100))  # Update progress bar
            self.update_remaining_videos.emit(total_files - (i + 1))  # Update remaining videos count

        self.update_status_bar.emit("Video processing completed.")  # Update status bar when done

    def is_video_file(self, file):
        """
        Check if the file is a video file based on its extension.
        """
        return file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))

    def is_h265(self, file_path):
        """
        Check if the video file is encoded in H.265 format using ffprobe.
        """
        try:
            result = subprocess.run(
                [self.ffprobe_path, '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_name', '-of', 'default=nw=1:nk=1', file_path],
                capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            return 'hevc' in result.stdout
        except FileNotFoundError as e:
            self.log_error(file_path, e)
            self.log_error(file_path, f"Environment PATH: {os.environ['PATH']}")
            raise e
        except subprocess.CalledProcessError as e:
            self.log_error(file_path, e)
            raise e

    def convert_to_h265_handbrake(self, file_path, use_gpu, use_amd):
        """
        Convert the video file to H.265 format using HandBrakeCLI.
        """
        output_file = sanitize_path(os.path.splitext(file_path)[0] + ".h265.mp4")
        handbrake_cli_path = sanitize_path(os.path.join(os.path.dirname(__file__), "resources", "HandBrakeCLI.exe"))
        if use_gpu:
            if use_amd:
                command = [handbrake_cli_path, '-i', file_path, '-o', output_file, '--encoder', 'vce_h265', '--audio', '1,1', '--aencoder', 'copy', '--optimize', '--no-markers']
            else:
                command = [handbrake_cli_path, '-i', file_path, '-o', output_file, '--encoder', 'nvenc_h265', '--audio', '1,1', '--aencoder', 'copy', '--optimize', '--no-markers']
        else:
            command = [handbrake_cli_path, '-i', file_path, '-o', output_file, '--encoder', 'x265', '--audio', '1,1', '--aencoder', 'copy', '--optimize', '--no-markers']

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW)
        while True:
            if self.stop_event:
                process.terminate()
                break
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                # Filter the output to include only specific lines or keywords
                if any(keyword in output for keyword in ["Encoding", "Progress", "Complete"]):
                    self.update_ffmpeg_output.emit(output.strip())

    def convert_to_h265_ffmpeg(self, file_path, use_gpu, use_amd):
        """
        Convert the video file to H.265 format using ffmpeg.
        """
        output_file = sanitize_path(os.path.splitext(file_path)[0] + ".h265.mp4")
        if use_gpu:
            if use_amd:
                command = [self.ffmpeg_path, '-i', file_path, '-c:v', 'hevc_amf', '-c:a', 'copy', output_file]
            else:
                command = [self.ffmpeg_path, '-i', file_path, '-c:v', 'hevc_nvenc', '-c:a', 'copy', output_file]
        else:
            command = [self.ffmpeg_path, '-i', file_path, '-c:v', 'libx265', '-c:a', 'copy', output_file]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW)
        while True:
            if self.stop_event:
                process.terminate()
                break
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                # Filter the output to include only specific lines or keywords
                if any(keyword in output for keyword in ["frame", "fps", "bitrate", "speed"]):
                    self.update_ffmpeg_output.emit(output.strip())

    def rename_and_cleanup(self, file_path):
        """
        Rename the converted file and move the original file to the recycle bin.
        """
        old_file = sanitize_path(file_path)
        new_file = sanitize_path(os.path.splitext(file_path)[0] + ".h265.mp4")
        final_file = sanitize_path(os.path.splitext(file_path)[0] + ".mp4")

        if os.path.exists(new_file):
            send2trash(old_file)
            os.rename(new_file, final_file)

    def log_error(self, file_path, error):
        """
        Log any errors that occur during processing to the error log file.
        """
        with open(self.error_log_file, 'a', encoding='utf-8') as log_file:
            log_file.write(f"{datetime.now()}: Error processing {file_path} - {error}\n")
            if isinstance(error, subprocess.CalledProcessError):
                log_file.write(f"Command: {error.cmd}\n")
                log_file.write(f"Return Code: {error.returncode}\n")
                log_file.write(f"Output: {error.output}\n")