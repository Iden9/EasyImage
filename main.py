from PIL import Image
import os
import subprocess
import tempfile
import platform
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QComboBox, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt


def create_icns(input_path, output_path):
    """
    创建ICNS文件（仅支持MacOS系统）
    :param input_path: 输入图片路径
    :param output_path: 输出ICNS文件路径
    """
    try:
        # 检查是否在MacOS系统上运行
        if platform.system() != 'Darwin':
            raise Exception("ICNS转换只支持MacOS系统")

        # 创建临时文件夹
        temp_dir = tempfile.mkdtemp()
        icon_set_path = os.path.join(temp_dir, 'icon.iconset')
        os.mkdir(icon_set_path)

        # 打开原始图片
        img = Image.open(input_path)

        # ICNS需要的尺寸列表
        sizes = [
            (16, '16x16'),
            (32, '16x16@2x'),
            (32, '32x32'),
            (64, '32x32@2x'),
            (128, '128x128'),
            (256, '128x128@2x'),
            (256, '256x256'),
            (512, '256x256@2x'),
            (512, '512x512'),
            (1024, '512x512@2x')
        ]

        # 生成不同尺寸的图片
        for size, name in sizes:
            resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
            icon_path = os.path.join(icon_set_path, f'icon_{name}.png')
            resized_img.save(icon_path)

        # 使用iconutil命令生成icns文件
        subprocess.run(['iconutil', '-c', 'icns', icon_set_path, '-o', output_path], check=True)

        # 清理临时文件
        subprocess.run(['rm', '-rf', temp_dir])
        print(f"ICNS转换成功: {output_path}")

    except Exception as e:
        print(f"ICNS转换失败: {str(e)}")


def convert_image(input_path, output_path, format):
    """
    转换图片格式
    :param input_path: 输入图片路径
    :param output_path: 输出图片路径
    :param format: 目标格式 (例如: 'ICO', 'PNG', 'JPEG', 'ICNS'等)
    """
    try:
        # 如果是ICNS格式，使用专门的转换函数
        if format.upper() == 'ICNS':
            create_icns(input_path, output_path)
            return

        # 打开图片
        img = Image.open(input_path)

        # 如果转换为ICO格式，需要特殊处理
        if format.upper() == 'ICO':
            # ICO格式需要特定的尺寸，这里设置为48x48
            img = img.resize((48, 48))

        # 保存为新格式
        img.save(output_path, format=format)
        print(f"转换成功: {output_path}")

    except Exception as e:
        print(f"转换失败: {str(e)}")


class ImageConverterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.input_path = None
        self.output_path = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('图片格式转换器')
        self.setGeometry(300, 300, 400, 200)

        # 创建中央部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 输入文件选择
        self.input_label = QLabel('未选择输入文件')
        input_btn = QPushButton('选择输入文件')
        input_btn.clicked.connect(self.select_input_file)

        # 输出文件选择
        self.output_label = QLabel('未选择输出文件')
        output_btn = QPushButton('选择输出位置')
        output_btn.clicked.connect(self.select_output_file)

        # 格式选择下拉框
        format_label = QLabel('选择输出格式:')
        self.format_combo = QComboBox()
        self.format_combo.addItems(['PNG', 'JPEG', 'ICO', 'ICNS'])
        # 添加格式改变时的处理
        self.format_combo.currentTextChanged.connect(self.on_format_changed)

        # 转换按钮
        convert_btn = QPushButton('开始转换')
        convert_btn.clicked.connect(self.start_conversion)

        # 添加部件到布局
        layout.addWidget(self.input_label)
        layout.addWidget(input_btn)
        layout.addWidget(self.output_label)
        layout.addWidget(output_btn)
        layout.addWidget(format_label)
        layout.addWidget(self.format_combo)
        layout.addWidget(convert_btn)

    def select_input_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, '选择输入文件', '',
            'Images (*.png *.jpg *.jpeg *.bmp *.ico *.icns)')
        if file_name:
            self.input_path = file_name
            self.input_label.setText(f'输入文件: {os.path.basename(file_name)}')

    def select_output_file(self):
        # 根据当前选择的格式设置文件过滤器和扩展名
        current_format = self.format_combo.currentText().lower()
        if current_format == 'jpeg':
            file_filter = 'Images (*.jpg)'
            default_ext = '.jpg'
        elif current_format == 'icns':
            file_filter = 'ICNS files (*.icns)'
            default_ext = '.icns'
        else:
            file_filter = f'Images (*.{current_format.lower()})'
            default_ext = f'.{current_format.lower()}'

        file_name, _ = QFileDialog.getSaveFileName(
            self, '选择输出位置', '',
            file_filter)
        
        if file_name:
            # 确保文件有正确的扩展名
            if not file_name.lower().endswith(default_ext):
                file_name += default_ext
            
            self.output_path = file_name
            self.output_label.setText(f'输出文件: {os.path.basename(file_name)}')

    def on_format_changed(self):
        # 当格式改变时，清除输出路径
        self.output_path = None
        self.output_label.setText('未选择输出文件')

    def start_conversion(self):
        if not self.input_path or not self.output_path:
            QMessageBox.warning(self, '警告', '请选择输入和输出文件')
            return

        try:
            convert_image(self.input_path, self.output_path, self.format_combo.currentText())
            QMessageBox.information(self, '成功', '转换完成！')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'转换失败: {str(e)}')


def main():
    app = QApplication([])
    window = ImageConverterGUI()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()