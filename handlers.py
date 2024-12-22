import os
from PySide6.QtWidgets import QFileDialog, QMessageBox
from photo_converting import ImageWorkerThread
from video_converting import VideoWorkerThread
from utils import sanitize_path

def browse_directory(dir_input):
    directory = QFileDialog.getExistingDirectory(None, "Select Directory")
    if directory:
        dir_input.setText(directory)

def start_image_conversion(widget):
    directory = sanitize_path(widget.dir_input.text())
    use_max_cores = widget.use_max_cores_checkbox.isChecked()
    if not os.path.isdir(directory):
        QMessageBox.warning(widget, "Invalid Directory", "Please enter a valid directory path.")
        return

    # Count the total number of image files
    total_photos = sum([len(files) for r, d, files in os.walk(directory) if any(file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')) for file in files)])
    widget.update_photo_counts(total_photos, total_photos)

    widget.worker_thread = ImageWorkerThread(directory, use_max_cores, 'convert')
    widget.worker_thread.update_status.connect(widget.update_status)
    widget.worker_thread.update_status_bar.connect(widget.update_status_bar)
    widget.worker_thread.update_progress.connect(widget.update_progress)
    widget.worker_thread.update_remaining_photos.connect(lambda remaining: widget.update_photo_counts(total_photos, remaining))
    widget.worker_thread.finished.connect(widget.on_finished)
    widget.worker_thread.start()
    widget.status_bar.showMessage("Starting image conversion...")

def start_metadata_removal(widget):
    directory = sanitize_path(widget.dir_input.text())
    use_max_cores = widget.use_max_cores_checkbox.isChecked()
    if not os.path.isdir(directory):
        QMessageBox.warning(widget, "Invalid Directory", "Please enter a valid directory path.")
        return

    # Count the total number of image files
    total_photos = sum([len(files) for r, d, files in os.walk(directory) if any(file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')) for file in files)])
    widget.update_photo_counts(total_photos, total_photos)

    widget.worker_thread = ImageWorkerThread(directory, use_max_cores, 'remove_metadata')
    widget.worker_thread.update_status.connect(widget.update_status)
    widget.worker_thread.update_status_bar.connect(widget.update_status_bar)
    widget.worker_thread.update_progress.connect(widget.update_progress)
    widget.worker_thread.update_remaining_photos.connect(lambda remaining: widget.update_photo_counts(total_photos, remaining))
    widget.worker_thread.finished.connect(widget.on_finished)
    widget.worker_thread.start()
    widget.status_bar.showMessage("Starting metadata removal...")

def stop_all_image_operations(widget):
    if widget.worker_thread is not None:
        widget.worker_thread.stop()

def start_video_processing(widget):
    directory = sanitize_path(widget.dir_input.text())
    use_gpu = widget.use_gpu_checkbox.isChecked()
    if not os.path.isdir(directory):
        QMessageBox.warning(widget, "Invalid Directory", "Please enter a valid directory path.")
        return

    # Count the total number of video files
    total_videos = sum([len(files) for r, d, files in os.walk(directory) if any(file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv')) for file in files)])
    widget.update_video_counts(total_videos, total_videos)

    widget.worker_thread = VideoWorkerThread(directory, use_gpu)
    widget.worker_thread.update_status.connect(widget.update_status)
    widget.worker_thread.update_status_bar.connect(widget.update_status_bar)
    widget.worker_thread.update_ffmpeg_output.connect(widget.update_ffmpeg_output)
    widget.worker_thread.update_progress.connect(widget.update_progress)
    widget.worker_thread.update_remaining_videos.connect(lambda remaining: widget.update_video_counts(total_videos, remaining))
    widget.worker_thread.finished.connect(widget.on_finished)
    widget.worker_thread.start()
    widget.status_bar.showMessage("Starting video processing...")

def stop_all_video_operations(widget):
    if widget.worker_thread is not None:
        widget.worker_thread.stop()