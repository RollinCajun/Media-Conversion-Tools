"""
Author: RollinCajun
Email: kastingwithfrostbyte@proton.me

Description:
This module contains the GUI widgets for image and video processing using PySide6.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QFileDialog, QTextEdit, QCheckBox, 
                               QProgressBar, QMessageBox, QStatusBar)
from PySide6.QtCore import Qt
from handlers import (browse_directory, start_image_conversion, start_metadata_removal, 
                      stop_all_image_operations, start_video_processing, stop_all_video_operations)
from PySide6.QtGui import QTextCursor

class ImageProcessingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.worker_thread = None

    def init_ui(self):
        layout = QVBoxLayout()

        # Directory input
        dir_layout = QHBoxLayout()
        dir_label = QLabel("Directory Path:")
        self.dir_input = QLineEdit("D:\\ffmpeg Conversion Folder")  # Set default folder path
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(lambda: browse_directory(self.dir_input))
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(browse_button)

        # Checkbox for using max CPU cores
        self.use_max_cores_checkbox = QCheckBox("Use Max CPU Cores")

        # Buttons for conversion and metadata removal
        button_layout = QHBoxLayout()
        convert_button = QPushButton("Convert to JPG and Add Comment")
        convert_button.clicked.connect(lambda: start_image_conversion(self))
        remove_metadata_button = QPushButton("Remove All Metadata")
        remove_metadata_button.clicked.connect(lambda: start_metadata_removal(self))
        stop_button = QPushButton("Stop All")
        stop_button.clicked.connect(lambda: stop_all_image_operations(self))
        button_layout.addWidget(convert_button)
        button_layout.addWidget(remove_metadata_button)
        button_layout.addWidget(stop_button)

        # Log text box
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)

        # Photo count labels
        count_layout = QHBoxLayout()
        self.total_photos_label = QLabel("Total Photos: 0")
        self.remaining_photos_label = QLabel("Remaining Photos: 0")
        count_layout.addWidget(self.total_photos_label)
        count_layout.addWidget(self.remaining_photos_label, alignment=Qt.AlignRight)

        # Status bar and progress bar
        self.status_bar = QStatusBar()
        self.progress_bar = QProgressBar()

        layout.addLayout(dir_layout)
        layout.addWidget(self.use_max_cores_checkbox)
        layout.addLayout(button_layout)
        layout.addLayout(count_layout)
        layout.addWidget(self.log_text)
        layout.addWidget(self.status_bar)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def update_status(self, message):
        # Append message to the log text box and scroll to the end
        self.log_text.append(message)
        self.log_text.moveCursor(QTextCursor.End)

    def update_status_bar(self, message):
        # Show message in the status bar
        self.status_bar.showMessage(message)

    def update_progress(self, value):
        # Update the progress bar value
        self.progress_bar.setValue(value)

    def update_photo_counts(self, total, remaining):
        # Update the total and remaining photo counts
        self.total_photos_label.setText(f"Total Photos: {total}")
        self.remaining_photos_label.setText(f"Remaining Photos: {remaining}")

    def on_finished(self):
        # Show completion message in the status bar
        self.status_bar.showMessage("Operation completed.")

class VideoProcessingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.worker_thread = None

    def init_ui(self):
        layout = QVBoxLayout()

        # Directory input
        dir_layout = QHBoxLayout()
        dir_label = QLabel("Directory Path:")
        self.dir_input = QLineEdit("D:\\ffmpeg Conversion Folder")  # Set default folder path
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(lambda: browse_directory(self.dir_input))
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(browse_button)

        # Checkbox for using GPU
        self.use_gpu_checkbox = QCheckBox("Use GPU")

        # Buttons for video processing
        button_layout = QHBoxLayout()
        process_button = QPushButton("Process Videos")
        process_button.clicked.connect(lambda: start_video_processing(self))
        stop_button = QPushButton("Stop All")
        stop_button.clicked.connect(lambda: stop_all_video_operations(self))
        button_layout.addWidget(process_button)
        button_layout.addWidget(stop_button)

        # Video count labels
        count_layout = QHBoxLayout()
        self.total_videos_label = QLabel("Total Videos: 0")
        self.remaining_videos_label = QLabel("Remaining Videos: 0")
        count_layout.addWidget(self.total_videos_label)
        count_layout.addWidget(self.remaining_videos_label, alignment=Qt.AlignRight)

        # Log text boxes
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.ffmpeg_output_text = QTextEdit()
        self.ffmpeg_output_text.setReadOnly(True)

        # Status bar and progress bar
        self.status_bar = QStatusBar()
        self.progress_bar = QProgressBar()

        layout.addLayout(dir_layout)
        layout.addWidget(self.use_gpu_checkbox)
        layout.addLayout(button_layout)
        layout.addLayout(count_layout)
        layout.addWidget(self.log_text)
        layout.addWidget(self.ffmpeg_output_text)
        layout.addWidget(self.status_bar)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def update_status(self, message):
        # Append message to the log text box and scroll to the end
        self.log_text.append(message)
        self.log_text.moveCursor(QTextCursor.End)

    def update_status_bar(self, message):
        # Show message in the status bar
        self.status_bar.showMessage(message)

    def update_ffmpeg_output(self, message):
        # Append ffmpeg output message to the ffmpeg log text box and scroll to the end
        self.ffmpeg_output_text.append(message)
        self.ffmpeg_output_text.moveCursor(QTextCursor.End)

    def update_progress(self, value):
        # Update the progress bar value
        self.progress_bar.setValue(value)

    def update_video_counts(self, total, remaining):
        # Update the total and remaining video counts
        self.total_videos_label.setText(f"Total Videos: {total}")
        self.remaining_videos_label.setText(f"Remaining Videos: {remaining}")

    def on_finished(self):
        # Show completion message in the status bar
        self.status_bar.showMessage("Operation completed.")