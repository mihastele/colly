import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QSlider, QLabel, QPushButton)
from PyQt5.QtCore import Qt
import platform
import ctypes
import math
from ctypes import windll, byref, c_ulong, c_ushort, Structure, c_void_p

# Windows-specific structures and constants
class RAMP(Structure):
    _fields_ = [('Red', c_ushort * 256),
                ('Green', c_ushort * 256),
                ('Blue', c_ushort * 256)]

class WindowsColorFilter:
    def __init__(self):
        self.original_ramp = RAMP()
        self.hdc = windll.gdi32.CreateDCW('DISPLAY', None, None, None)
        # Store original gamma ramp
        windll.gdi32.GetDeviceGammaRamp(self.hdc, byref(self.original_ramp))

    def apply_filter(self, temperature, brightness):
        # Convert temperature to RGB values
        temp = temperature / 100.0
        if temp <= 66:
            red = 255
            green = temp
            green = 99.4708025861 * math.log(green) - 161.1195681661
            if temp <= 19:
                blue = 0
            else:
                blue = temp - 10
                blue = 138.5177312231 * math.log(blue) - 305.0447927307
        else:
            red = temp - 60
            red = 329.698727446 * math.pow(red, -0.1332047592)
            green = temp - 60
            green = 288.1221695283 * math.pow(green, -0.0755148492)
            blue = 255

        # Clamp values
        red = max(0, min(255, red)) * brightness
        green = max(0, min(255, green)) * brightness
        blue = max(0, min(255, blue)) * brightness

        # Create gamma ramp
        ramp = RAMP()
        for i in range(256):
            ramp.Red[i] = min(65535, int((i * red / 255) * 256))
            ramp.Green[i] = min(65535, int((i * green / 255) * 256))
            ramp.Blue[i] = min(65535, int((i * blue / 255) * 256))

        # Apply the gamma ramp
        windll.gdi32.SetDeviceGammaRamp(self.hdc, byref(ramp))

    def reset(self):
        # Restore original gamma ramp
        windll.gdi32.SetDeviceGammaRamp(self.hdc, byref(self.original_ramp))

    def cleanup(self):
        # Reset and cleanup
        self.reset()
        windll.gdi32.DeleteDC(self.hdc)

class BlueFilterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Blue Light Filter')
        self.setGeometry(100, 100, 400, 300)
        
        # Initialize Windows color filter
        self.windows_filter = WindowsColorFilter()
        
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
        if self.is_enabled:
            self.apply_filter()
        else:
            self.windows_filter.reset()

    def apply_filter(self):
        temp = self.temp_slider.value()
        brightness = self.brightness_slider.value() / 100.0
        self.windows_filter.apply_filter(temp, brightness)

    def closeEvent(self, event):
        self.windows_filter.cleanup()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BlueFilterApp()
    window.show()
    sys.exit(app.exec_())
