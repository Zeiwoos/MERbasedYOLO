#进行jupyter文件的调试请使用vscode，否则使用pycharm community

#建议使用labelimg(cmd进入环境后labelimg)进行图片集打标，或者labelquick

#由于本人计算机性能不足，模型利用AutoDL提供的服务进行训练

import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
