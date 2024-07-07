# main.py
import sys
import os
import shutil
import subprocess
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QTextEdit
)
from PySide6.QtCore import QProcess
from PySide6.QtGui import QFont

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("图片上传与分析界面")
        self.setGeometry(300, 300, 800, 600)

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

        main_layout.addLayout(button_layout)

        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.output_display.setFont(QFont("Courier", 10))
        main_layout.addWidget(self.output_display)

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
        """)

    def upload_image(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "选择图片", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)", options=options)
        if files:
            save_dir = os.path.join(os.getcwd(), 'data', 'images')
            os.makedirs(save_dir, exist_ok=True)
            for file in files:
                try:
                    shutil.copy(file, save_dir)
                    QMessageBox.information(self, "成功", f"图片已保存到 {save_dir}")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"无法保存图片: {e}")

    def upload_training_data(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "选择训练数据", "", "Data files (*)", options=options)
        if files:
            save_dir = os.path.join(os.getcwd(), 'mydataset')
            os.makedirs(save_dir, exist_ok=True)
            for file in files:
                try:
                    shutil.copy(file, save_dir)
                    QMessageBox.information(self, "成功", f"训练数据已保存到 {save_dir}")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"无法保存训练数据: {e}")

    def run_detect(self):
        self.output_display.clear()
        self.detect_process.start(sys.executable, ["detect.py"])

    def run_train(self):
        self.output_display.clear()
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
        self.output_display.append(stdout)

    def handle_detect_stderr(self):
        data = self.detect_process.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.output_display.append(stderr)

    def handle_train_stdout(self):
        data = self.train_process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.output_display.append(stdout)

    def handle_train_stderr(self):
        data = self.train_process.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.output_display.append(stderr)

    def process_finished(self):
        QMessageBox.information(self, "完成", "脚本已运行完毕")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
