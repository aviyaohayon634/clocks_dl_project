import sys
import os
import csv
from datetime import datetime
import random
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import QTimer, QTime, Qt, QSize, QRect
from PyQt5.QtGui import QFont, QFontDatabase, QFontMetrics, QPixmap, QPainter, QColor, QPen, QBrush

# Available fonts
FONTS = [
    "ATOMICCLOCKRADIO.TTF",
    "Clocky Stick.otf",
    "digital-7.ttf",
    "digital-clock.ttf",
    "Super Mindset.ttf",
    "wwDigital.ttf"
]

def get_contrasting_color(bg_color):
    """Get a contrasting text color for the given background color"""
    # Convert to HSL for better contrast calculation
    bg_hue = bg_color.hueF()
    bg_sat = bg_color.saturationF()
    bg_light = bg_color.lightnessF()

    # If background is dark, use light text; if light, use dark text
    if bg_light < 0.5:
        return QColor.fromHslF(bg_hue, min(bg_sat + 0.3, 1.0), min(bg_light + 0.5, 1.0))
    else:
        return QColor.fromHslF(bg_hue, min(bg_sat + 0.3, 1.0), max(bg_light - 0.5, 0.0))

class DigitalClock(QWidget):
    def __init__(self, time_str=None, font_name=None, bg_color=None, text_color=None, show_design=True):
        super().__init__()
        self.time_label = QLabel(self)
        self.current_time = time_str
        self.font_name = font_name
        self.bg_color = bg_color or QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.text_color = text_color or get_contrasting_color(self.bg_color)
        self.show_design = show_design
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Digital Clock")
        self.setFixedSize(1100, 300)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(20, 20, 20, 20)
        vbox.setSpacing(0)
        vbox.addWidget(self.time_label)
        self.setLayout(vbox)

        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set colors
        bg_color_str = f"rgb({self.bg_color.red()}, {self.bg_color.green()}, {self.bg_color.blue()})"
        text_color_str = f"rgb({self.text_color.red()}, {self.text_color.green()}, {self.text_color.blue()})"

        self.time_label.setStyleSheet(f"font-size: 170px; color: {text_color_str};")
        self.setStyleSheet(f"background-color: {bg_color_str};")

        # Load random font
        self.label_font_family = None
        if self.font_name:
            try:
                font_path = os.path.join("fonts", self.font_name)
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    self.label_font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            except:
                self.label_font_family = None

        self.update_time()

    def set_font_size_to_fit(self, text):
        font_family = self.label_font_family or self.time_label.font().family()
        font_size = 170
        font = QFont(font_family, font_size)
        metrics = QFontMetrics(font)
        max_width = self.width() - 60

        while font_size > 30 and metrics.horizontalAdvance(text) > max_width:
            font_size -= 4
            font.setPointSize(font_size)
            metrics = QFontMetrics(font)

        self.time_label.setFont(font)

    def update_time(self):
        if self.current_time:
            current_time = self.current_time
        else:
            current_time = QTime.currentTime().toString("hh:mm:ss AP")

        self.set_font_size_to_fit(current_time)
        self.time_label.setText(current_time)

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.show_design:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get the time components for design elements
        time_parts = self.time_label.text().split(':')
        if len(time_parts) == 3:
            hours, minutes, seconds = time_parts

            # Calculate positions for rectangles around time components
            label_rect = self.time_label.geometry()
            time_width = label_rect.width()
            component_width = time_width // 3

            # Draw rectangles around each time component
            pen = QPen(self.text_color, 3)
            painter.setPen(pen)
            painter.setBrush(QBrush(Qt.NoBrush))

            for i in range(3):
                x = label_rect.x() + i * component_width
                y = label_rect.y()
                width = component_width - 10
                height = label_rect.height()

                rect = QRect(x, y, width, height)
                painter.drawRoundedRect(rect, 10, 10)

                # Add small dots or separators
                if i < 2:
                    sep_x = x + width + 5
                    sep_y = y + height // 2
                    painter.drawEllipse(sep_x - 3, sep_y - 3, 6, 6)

    def take_screenshot(self, filename):
        # Ensure layout is up-to-date before rendering
        self.show()
        QApplication.processEvents()

        pixmap = self.grab()
        pixmap.save(filename, "PNG")
        self.hide()


def generate_clock_data(num_designs=6, times_per_design=250, output_dir="clock_screenshots", csv_file="clock_times.csv"):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Create 10 random designs upfront
    designs = []
    for design_id in range(num_designs):
        design = {
            'design_id': design_id,
            'font': random.choice(FONTS),
            'bg_color': QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
            'show_design': random.choice([True, False])
        }
        design['text_color'] = get_contrasting_color(design['bg_color'])
        designs.append(design)

    print(f"Created {num_designs} designs")

    # Initialize CSV file
    with open(csv_file, 'w', newline='') as csvfile:
        fieldnames = ['sample_id', 'design_id', 'filename', 'hour', 'minute', 'second', 'time_string', 'font', 'bg_color', 'text_color', 'has_design']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Create QApplication once
        app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()

        sample_id = 0
        # For each design, generate 300 different times
        for design in designs:
            print(f"\nGenerating times for design {design['design_id'] + 1}/{num_designs}...")

            # Generate 300 unique time combinations for this design
            times_generated = set()
            while len(times_generated) < times_per_design:
                hour = random.randint(0, 23)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                time_tuple = (hour, minute, second)

                if time_tuple not in times_generated:
                    times_generated.add(time_tuple)

                    time_str = f"{hour:02d}:{minute:02d}:{second:02d}"

                    # Create clock widget with current design
                    clock = DigitalClock(
                        time_str=time_str,
                        font_name=design['font'],
                        bg_color=design['bg_color'],
                        text_color=design['text_color'],
                        show_design=design['show_design']
                    )

                    # Take screenshot
                    filename = f"{output_dir}/digital_clock_{sample_id:05d}.png"
                    clock.take_screenshot(filename)

                    # Write to CSV
                    writer.writerow({
                        'sample_id': sample_id,
                        'design_id': design['design_id'],
                        'filename': filename,
                        'hour': hour,
                        'minute': minute,
                        'second': second,
                        'time_string': time_str,
                        'font': design['font'],
                        'bg_color': f"rgb({design['bg_color'].red()}, {design['bg_color'].green()}, {design['bg_color'].blue()})",
                        'text_color': f"rgb({design['text_color'].red()}, {design['text_color'].green()}, {design['text_color'].blue()})",
                        'has_design': design['show_design']
                    })

                    sample_id += 1

                    if sample_id % 50 == 0:
                        print(f"  Generated {len(times_generated)}/{times_per_design} times for this design...")

                    # Clean up
                    clock.close()

    total_samples = num_designs * times_per_design
    print(f"\nGenerated {total_samples} clock screenshots and saved to {csv_file}")

if __name__ == "__main__":
    # Generate 6 designs with 250 times each = 1500 total samples
    generate_clock_data(num_designs=6, times_per_design=250)