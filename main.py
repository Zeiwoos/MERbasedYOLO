
import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

# CASME数据集全部都是正脸，训练结果疑似有点过拟合
#
#训练步骤：
#准备好数据集，数据集的目录结构如下：
#train:images+labels     val:images+labels     比例：约8:2
#修改yaml文件，设置数据集路径
#修改train.py文件，设置训练参数（主要是yaml文件路径）