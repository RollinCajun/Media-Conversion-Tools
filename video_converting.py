import os
import subprocess
import time
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

    def __init__(self, directory, use_gpu, use_handbrake, use_amd, codec):
        super().__init__()
        self.directory = sanitize_path(directory)  # Sanitize the directory path
        self.use_gpu = use_gpu  # Flag to use GPU for processing
        self.use_handbrake = use_handbrake  # Flag to use HandBrakeCLI
        self.use_amd = use_amd  # Flag to use AMD encoding
        self.codec = codec  # Codec to use for conversion ('h265' or 'h264')
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
        temp_suffixes = (".h265.mp4", ".h264.mp4", ".h265.mkv", ".h264.mkv", ".h265", ".h264")
        for root, _, files in os.walk(directory):
            for file in files:
                lower_name = file.lower()
                if lower_name.endswith(temp_suffixes):
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

            self.update_status_bar.emit(f"Checking file: {file_path}")  # Debug log
            if self.needs_conversion(file_path, self.codec):
                self.update_status_bar.emit(f"Processing {file_path}")
                try:
                    if not self.is_correct_container(file_path):
                        self.update_status_bar.emit(f"Remuxing {file_path} to correct MP4 container...")
                        self.remux_to_mp4_container(file_path)
                        self.rename_and_cleanup(file_path, 'remuxed')
                        self.update_status.emit(f"{file_path} remuxed to correct MP4 container!")
                        file_path = sanitize_path(os.path.splitext(file_path)[0] + ".mp4")

                    if self.needs_conversion(file_path, self.codec):
                        self.update_status_bar.emit(f"Converting {file_path} to {self.codec.upper()}...")
                        if use_handbrake:
                            self.convert_with_handbrake(file_path, use_gpu, use_amd, self.codec)
                        else:
                            self.convert_with_ffmpeg(file_path, use_gpu, use_amd, self.codec)
                        self.rename_and_cleanup(file_path, self.codec)
                        self.update_status.emit(f"{file_path} converted to {self.codec.upper()}!")
                    else:
                        self.update_status.emit(f"Skipping {file_path}, already {self.codec.upper()} with compatible audio")
                        self.update_status_bar.emit(f"Skipping {file_path}, already {self.codec.upper()} with compatible audio")
                except Exception as e:
                    self.log_error(file_path, e)  # Log any errors
                    self.update_status.emit(f"Error converting {file_path}: {e}")
            else:
                if not file_path.lower().endswith('.mp4'):
                    self.update_status_bar.emit(f"Remuxing {file_path} to correct MP4 container without re-encoding...")
                    self.remux_to_mp4_container(file_path)
                    self.rename_and_cleanup(file_path, 'remuxed')
                    self.update_status.emit(f"{file_path} remuxed to correct MP4 container!")
                else:
                    self.update_status.emit(f"Skipping {file_path}, already {self.codec.upper()} with compatible audio")
                    self.update_status_bar.emit(f"Skipping {file_path}, already {self.codec.upper()} with compatible audio")

            self.update_ffmpeg_output.emit(f"Progress: {i + 1}/{total_files}")  # Update ffmpeg output
            self.update_progress.emit(int((i + 1) / total_files * 100))  # Update progress bar
            self.update_remaining_videos.emit(total_files - (i + 1))  # Update remaining videos count

        self.update_status_bar.emit("Video processing completed.")  # Update status bar when done

    def is_video_file(self, file):
        """
        Check if the file is a video file based on its extension.
        """
        return file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))

    def is_codec(self, file_path, codec):
        """
        Check if the video file is encoded in the specified codec format using ffprobe.
        """
        try:
            self.update_status_bar.emit(f"Checking codec for: {file_path}")  # Debug log
            result = subprocess.run(
                [self.ffprobe_path, '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_name', '-of', 'default=nw=1:nk=1', file_path],
                capture_output=True, text=True, encoding='utf-8', errors='replace', check=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            detected_codec = result.stdout.strip().lower()
            self.update_status_bar.emit(f"Codec check result for {file_path}: {detected_codec}")  # Debug log
            if codec == 'h265':
                return detected_codec in ('hevc', 'h265')
            if codec == 'h264':
                return detected_codec == 'h264'
            return False
        except FileNotFoundError as e:
            self.log_error(file_path, e)
            self.log_error(file_path, f"Environment PATH: {os.environ['PATH']}")
            raise e
        except subprocess.CalledProcessError as e:
            self.log_error(file_path, e)
            self.log_error(file_path, f"ffprobe error output: {e.stderr}")
            return False
        except Exception as e:
            self.log_error(file_path, e)
            return False

    def get_audio_codec(self, file_path):
        """
        Return the codec name for the first audio stream in the file.
        """
        try:
            result = subprocess.run(
                [self.ffprobe_path, '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=codec_name', '-of', 'default=nw=1:nk=1', file_path],
                capture_output=True, text=True, encoding='utf-8', errors='replace', check=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            audio_codec = result.stdout.strip().lower()
            if audio_codec:
                self.update_status_bar.emit(f"Audio codec check result for {file_path}: {audio_codec}")
                return audio_codec
            return None
        except subprocess.CalledProcessError as e:
            self.update_status_bar.emit(f"Audio codec check failed for {file_path}: {e.stderr.strip()}")
            return None
        except Exception as e:
            self.log_error(file_path, e)
            return None

    def is_default_audio(self, audio_codec):
        """
        Determine whether the audio codec is the default platform-compatible codec.
        """
        return audio_codec in ('aac', 'aac_latm')

    def get_format_name(self, file_path):
        """
        Return the container format name (e.g., 'matroska', 'mov,mp4,m4a,3gp,3g2,mj2', etc.).
        """
        try:
            result = subprocess.run(
                [self.ffprobe_path, '-v', 'error', '-show_entries', 'format=format_name', '-of', 'default=nw=1:nk=1', file_path],
                capture_output=True, text=True, encoding='utf-8', errors='replace', check=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            format_name = result.stdout.strip().lower()
            if format_name:
                self.update_status_bar.emit(f"Format detected for {file_path}: {format_name}")
                return format_name
            return None
        except subprocess.CalledProcessError:
            return None
        except Exception as e:
            self.log_error(file_path, e)
            return None

    def is_correct_container(self, file_path):
        """
        Check if the file has the correct container format for its extension.
        MP4 files should be in mov,mp4,m4a,3gp,3g2,mj2 format, not matroska.
        """
        if not file_path.lower().endswith('.mp4'):
            return True

        format_name = self.get_format_name(file_path)
        if format_name is None:
            return True

        if 'matroska' in format_name:
            self.update_status_bar.emit(f"File {file_path} has incorrect container (matroska in mp4), will remux to correct format")
            return False

        return True

    def needs_conversion(self, file_path, codec):
        """
        Determine whether the video needs conversion because the video codec, audio codec, or container format is not compatible.
        """
        if not self.is_correct_container(file_path):
            return True

        if not self.is_codec(file_path, codec):
            return True

        audio_codec = self.get_audio_codec(file_path)
        if audio_codec is None:
            return False

        if not self.is_default_audio(audio_codec):
            self.update_status_bar.emit(f"Audio codec {audio_codec} is not default for {file_path}, converting audio to AAC")
            return True

        return False

    def convert_with_handbrake(self, file_path, use_gpu, use_amd, codec):
        """
        Convert the video file to the specified codec format using HandBrakeCLI.
        """
        output_file = sanitize_path(os.path.splitext(file_path)[0] + f".{codec}.mp4")
        handbrake_cli_path = sanitize_path(os.path.join(os.path.dirname(__file__), "resources", "HandBrakeCLI.exe"))
        encoder = 'x265' if codec == 'h265' else 'x264'
        if use_gpu:
            if use_amd:
                encoder = 'vce_h265' if codec == 'h265' else 'vce_h264'
            else:
                encoder = 'nvenc_h265' if codec == 'h265' else 'nvenc_h264'
        command = [handbrake_cli_path, '-i', file_path, '-o', output_file, '--encoder', encoder, '--audio', '1,1', '--aencoder', 'av_aac', '--optimize', '--no-markers']

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
        try:
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
        finally:
            if process.stdout is not None:
                process.stdout.close()
            process.wait()

    def remux_to_mp4_container(self, file_path):
        """
        Remux video/audio streams to correct MP4 container without re-encoding.
        """
        output_file = sanitize_path(os.path.splitext(file_path)[0] + ".remuxed.mp4")
        command = [
            self.ffmpeg_path, '-i', file_path,
            '-c:v', 'copy', '-c:a', 'copy', '-movflags', '+faststart', output_file
        ]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            while True:
                if self.stop_event:
                    process.terminate()
                    break
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    if any(keyword in output for keyword in ["frame", "fps", "bitrate", "speed"]):
                        self.update_ffmpeg_output.emit(output.strip())
        finally:
            if process.stdout is not None:
                process.stdout.close()
            process.wait()

        if not os.path.exists(output_file):
            raise FileNotFoundError(f"Remuxing failed: Output file not created for {file_path}")

    def convert_with_ffmpeg(self, file_path, use_gpu, use_amd, codec):
        """
        Convert the video file to the specified codec format using ffmpeg.
        """
        output_file = sanitize_path(os.path.splitext(file_path)[0] + f".{codec}.mp4")
        if codec == 'h265':
            if use_gpu:
                encoder = 'hevc_nvenc'
                command = [
                    self.ffmpeg_path, '-hwaccel', 'cuda', '-i', file_path,
                    '-c:v', encoder, '-preset', 'medium', '-cq', '23', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', output_file
                ]
            else:
                encoder = 'libx265'
                command = [
                    self.ffmpeg_path, '-i', file_path,
                    '-c:v', encoder, '-preset', 'medium', '-crf', '23', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', output_file
                ]
        else:  # codec == 'h264'
            if use_gpu:
                encoder = 'h264_nvenc'
                command = [
                    self.ffmpeg_path, '-hwaccel', 'cuda', '-i', file_path,
                    '-c:v', encoder, '-preset', 'medium', '-cq', '23', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', output_file
                ]
            else:
                encoder = 'libx264'
                command = [
                    self.ffmpeg_path, '-i', file_path,
                    '-c:v', encoder, '-preset', 'medium', '-crf', '23', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', output_file
                ]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
        try:
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
        finally:
            if process.stdout is not None:
                process.stdout.close()
            process.wait()

        # Verify if the output file was created
        if not os.path.exists(output_file):
            raise FileNotFoundError(f"Conversion failed: Output file not created for {file_path}")

    def rename_and_cleanup(self, file_path, codec):
        """
        Remove the original file, then rename the converted file to the original file name.
        """
        old_file = sanitize_path(file_path)
        if codec == 'remuxed':
            converted_candidate_mkv = None
            converted_candidate_mp4 = sanitize_path(os.path.splitext(file_path)[0] + ".remuxed.mp4")
        else:
            converted_candidate_mkv = sanitize_path(os.path.splitext(file_path)[0] + f".{codec}.mkv")
            converted_candidate_mp4 = sanitize_path(os.path.splitext(file_path)[0] + f".{codec}.mp4")
        final_file = sanitize_path(os.path.splitext(file_path)[0] + ".mp4")

        if converted_candidate_mkv and os.path.exists(converted_candidate_mkv):
            new_file = converted_candidate_mkv
        elif os.path.exists(converted_candidate_mp4):
            new_file = converted_candidate_mp4
        else:
            self.update_status.emit(f"Error: Converted file not found for {file_path}. Skipping cleanup.")
            return

        if os.path.exists(old_file):
            for attempt in range(5):
                try:
                    send2trash(old_file)
                    self.update_status_bar.emit(f"Moved original to recycle bin: {old_file}")
                    break
                except OSError as e:
                    if attempt == 4:
                        raise
                    time.sleep(0.2)

        os.replace(new_file, final_file)
        self.update_status_bar.emit(f"Converted and renamed {new_file} to {final_file}")

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