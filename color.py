import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QSlider, QLabel, QPushButton)
from PyQt5.QtCore import Qt
import platform
import subprocess

class BlueFilterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Blue Light Filter')
        self.setGeometry(100, 100, 400, 300)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        
        # Temperature slider
        temp_layout = QHBoxLayout()
        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setMinimum(2000)
        self.temp_slider.setMaximum(6500)
        self.temp_slider.setValue(6500)
        self.temp_slider.valueChanged.connect(self.update_temperature)
        
        temp_label = QLabel('Color Temperature (K):')
        self.temp_value = QLabel('6500')
        
        temp_layout.addWidget(temp_label)
        temp_layout.addWidget(self.temp_slider)
        temp_layout.addWidget(self.temp_value)
        
        # Brightness slider
        brightness_layout = QHBoxLayout()
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setMinimum(10)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(100)
        self.brightness_slider.valueChanged.connect(self.update_brightness)
        
        brightness_label = QLabel('Brightness (%):')
        self.brightness_value = QLabel('100')
        
        brightness_layout.addWidget(brightness_label)
        brightness_layout.addWidget(self.brightness_slider)
        brightness_layout.addWidget(self.brightness_value)
        
        # Enable/Disable button
        self.toggle_button = QPushButton('Enable Filter')
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self.toggle_filter)
        
        # Add all widgets to main layout
        layout.addLayout(temp_layout)
        layout.addLayout(brightness_layout)
        layout.addWidget(self.toggle_button)
        
        main_widget.setLayout(layout)
        
        self.is_enabled = False
        self.os_type = platform.system()

    def update_temperature(self):
        value = self.temp_slider.value()
        self.temp_value.setText(str(value))
        if self.is_enabled:
            self.apply_filter()

    def update_brightness(self):
        value = self.brightness_slider.value()
        self.brightness_value.setText(str(value))
        if self.is_enabled:
            self.apply_filter()

    def toggle_filter(self):
        self.is_enabled = self.toggle_button.isChecked()
        self.toggle_button.setText('Disable Filter' if self.is_enabled else 'Enable Filter')
        self.apply_filter()

    def apply_filter(self):
        if self.os_type == 'Linux':
            self.apply_linux_filter()
        elif self.os_type == 'Windows':
            self.apply_windows_filter()

    def apply_linux_filter(self):
        if self.is_enabled:
            temp = self.temp_slider.value()
            brightness = self.brightness_slider.value() / 100
            subprocess.run(['redshift', '-O', str(temp), '-b', str(brightness)])
        else:
            subprocess.run(['redshift', '-x'])

    def apply_windows_filter(self):
        # suggestion: Windows Display API
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BlueFilterApp()
    window.show()
    sys.exit(app.exec_())