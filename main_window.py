import os
import sys
import shutil
import subprocess
import re
import cv2
from PySide6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QTextEdit, QProgressBar, QStackedWidget, QLabel
)
from PySide6.QtCore import QProcess, Qt, QTimer
from PySide6.QtGui import QFont, QImage, QPixmap

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Osprey")
        self.setGeometry(300, 300, 800, 600)

        self.stacked_widget = QStackedWidget()
        self.initUI()

        self.detect_process = QProcess(self)
        self.detect_process.readyReadStandardOutput.connect(self.handle_detect_stdout)
        self.detect_process.readyReadStandardError.connect(self.handle_detect_stderr)
        self.detect_process.finished.connect(self.process_finished)

        self.train_process = QProcess(self)
        self.train_process.readyReadStandardOutput.connect(self.handle_train_stdout)
        self.train_process.readyReadStandardError.connect(self.handle_train_stderr)
        self.train_process.finished.connect(self.process_finished)

    def initUI(self):
        main_layout = QVBoxLayout()

        button_layout = QHBoxLayout()
        self.image_page_button = QPushButton("图片检测页面")
        self.image_page_button.clicked.connect(self.show_image_page)
        button_layout.addWidget(self.image_page_button)

        self.video_page_button = QPushButton("视频页面")
        self.video_page_button.clicked.connect(self.show_video_page)
        button_layout.addWidget(self.video_page_button)

        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.stacked_widget)

        self.init_image_page()
        self.init_video_page()

        self.setLayout(main_layout)

        # 设置样式
        self.setStyleSheet("""
            QWidget {
                background-color: #20b2aa;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
            QTextEdit {
                background-color: #fff5ee;
                border: 1px solid #CCCCCC;
                padding: 10px;
            }
            QProgressBar {
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 20px;
            }
        """)

    def init_image_page(self):
        self.image_page = QWidget()
        layout = QVBoxLayout()

        button_layout = QHBoxLayout()

        self.upload_button = QPushButton("增加测试图片")
        self.upload_button.clicked.connect(self.upload_image)
        button_layout.addWidget(self.upload_button)

        self.analyze_button = QPushButton("检测")
        self.analyze_button.clicked.connect(self.run_detect)
        button_layout.addWidget(self.analyze_button)

        self.open_results_button = QPushButton("打开分析结果")
        self.open_results_button.clicked.connect(self.open_results_folder)
        button_layout.addWidget(self.open_results_button)

        self.upload_train_button = QPushButton("训练数据集上传")
        self.upload_train_button.clicked.connect(self.upload_training_data)
        button_layout.addWidget(self.upload_train_button)

        self.train_button = QPushButton("训练")
        self.train_button.clicked.connect(self.run_train)
        button_layout.addWidget(self.train_button)

        layout.addLayout(button_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.output_display.setFont(QFont("Courier", 10))
        layout.addWidget(self.output_display)

        self.image_page.setLayout(layout)
        self.stacked_widget.addWidget(self.image_page)

    def init_video_page(self):
        self.video_page = QWidget()
        layout = QVBoxLayout()

        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.video_label)

        self.start_video_button = QPushButton("启动摄像头")
        self.start_video_button.clicked.connect(self.start_video)
        layout.addWidget(self.start_video_button)

        self.stop_video_button = QPushButton("停止摄像头")
        self.stop_video_button.clicked.connect(self.stop_video)
        layout.addWidget(self.stop_video_button)

        self.video_page.setLayout(layout)
        self.stacked_widget.addWidget(self.video_page)

    def show_image_page(self):
        self.stacked_widget.setCurrentWidget(self.image_page)

    def show_video_page(self):
        self.stacked_widget.setCurrentWidget(self.video_page)

    def upload_image(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "选择图片", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)", options=options)
        if files:
            save_dir = os.path.join(os.getcwd(), 'data', 'images')
            os.makedirs(save_dir, exist_ok=True)
            self.progress_bar.setValue(0)
            self.progress_bar.setMaximum(len(files))
            for i, file in enumerate(files):
                try:
                    shutil.copy(file, save_dir)
                    self.progress_bar.setValue(i + 1)
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"无法保存图片: {e}")
                    break
            QMessageBox.information(self, "成功", f"图片已保存到 {save_dir}")

    def upload_training_data(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "选择训练数据", "", "Data files (*)", options=options)
        if files:
            save_dir = os.path.join(os.getcwd(), 'mydataset')
            os.makedirs(save_dir, exist_ok=True)
            self.progress_bar.setValue(0)
            self.progress_bar.setMaximum(len(files))
            for i, file in enumerate(files):
                try:
                    shutil.copy(file, save_dir)
                    self.progress_bar.setValue(i + 1)
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"无法保存训练数据: {e}")
                    break
            QMessageBox.information(self, "成功", f"训练数据已保存到 {save_dir}")

    def run_detect(self):
        self.output_display.clear()
        self.progress_bar.setValue(0)
        self.detect_process.start(sys.executable, ["detect.py"])

    def run_train(self):
        self.output_display.clear()
        self.progress_bar.setValue(0)
        self.train_process.start(sys.executable, ["train.py"])

    def open_results_folder(self):
        result_dir = os.path.join(os.getcwd(), 'runs', 'detect')
        if os.path.exists(result_dir):
            if sys.platform == "win32":
                os.startfile(result_dir)
            elif sys.platform == "darwin":
                subprocess.call(["open", result_dir])
            else:
                subprocess.call(["xdg-open", result_dir])
        else:
            QMessageBox.critical(self, "错误", f"文件夹 {result_dir} 不存在")

    def handle_detect_stdout(self):
        data = self.detect_process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        stdout = self.remove_ansi_escape_sequences(stdout)
        self.output_display.append(stdout)
        self.update_progress(stdout)

    def handle_detect_stderr(self):
        data = self.detect_process.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        stderr = self.remove_ansi_escape_sequences(stderr)
        self.output_display.append(stderr)

    def handle_train_stdout(self):
        data = self.train_process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        stdout = self.remove_ansi_escape_sequences(stdout)
        self.output_display.append(stdout)

    def handle_train_stderr(self):
        data = self.train_process.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        stderr = self.remove_ansi_escape_sequences(stderr)
        self.output_display.append(stderr)

    def process_finished(self):
        self.progress_bar.setValue(100)
        QMessageBox.information(self, "完成", "脚本已运行完毕")

    def update_progress(self, text):
        match = re.search(r'image (\d+)/(\d+)', text)
        if match:
            current = int(match.group(1))
            total = int(match.group(2))
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(current)

    def remove_ansi_escape_sequences(self, text):
        ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', text)

    def start_video(self):
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(20)

    def stop_video(self):
        self.timer.stop()
        self.cap.release()
        self.video_label.clear()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(q_img))
