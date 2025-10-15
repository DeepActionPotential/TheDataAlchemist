import sys
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QSpinBox, QPushButton, 
                             QProgressBar, QCheckBox, QFileDialog, QMessageBox, QFrame,
                             QGroupBox, QSizePolicy)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QPoint
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QPainter
from PyQt5.QtCore import QLocale
from PyQt5.QtCore import QLocale, Qt


# Worker thread to prevent UI freezing
class ConversionThread(QThread):
    progress_updated = pyqtSignal(int)
    conversion_finished = pyqtSignal(bool)
    
    def __init__(self, conversion_function, kwargs):
        super().__init__()
        self.conversion_function = conversion_function
        self.kwargs = kwargs
        
    def run(self):
        try:
            success = self.conversion_function(**self.kwargs)
            self.conversion_finished.emit(success)
        except Exception as e:
            print(f"Error during conversion: {e}")
            self.conversion_finished.emit(False)


class SquareFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            SquareFrame {
                background: rgba(35, 35, 45, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)


class SquareButton(QPushButton):
    def __init__(self, icon_path=None, text="", tooltip_text="", parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(tooltip_text)
        self.setFixedSize(120, 40)
        self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        self.setStyleSheet("QPushButton { font-smoothing: antialiased; }")

        
        # ✅ Force the same smooth font as labels
        self.setFont(QFont("Segoe UI", 8, QFont.Bold))
        
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(20, 20))
        
        if text:
            self.setText(text)
        
        
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(60, 60, 70, 0.9);
                color: white;
                border: 1px solid rgba(79, 143, 240, 0.3);
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(79, 143, 240, 0.7);
                border: 1px solid rgba(79, 143, 240, 0.9);
            }
            QPushButton:pressed {
                background-color: rgba(79, 143, 240, 0.9);
            }
            QPushButton:disabled {
                background-color: rgba(50, 50, 60, 0.7);
                border: 1px solid rgba(100, 100, 110, 0.3);
                color: rgba(150, 150, 150, 0.7);
            }
        """)


class SquareProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(True)
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Segoe UI", 9))
        
        # Custom style for square look
        self.setStyleSheet("""
            QProgressBar {
                background-color: rgba(40, 40, 50, 0.9);
                border: 1px solid rgba(79, 143, 240, 0.3);
                text-align: center;
                color: white;
                font-weight: bold;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: rgba(79, 143, 240, 0.9);
            }
        """)


class UI(QMainWindow):
    def __init__(self, convert_dataset_to_report):
        super().__init__()
        self._drag_active = False
        self._drag_position = QPoint()
        self.convert_dataset_to_report = convert_dataset_to_report
        self.setGeometry(400, 200, 800, 650)
        
        # Remove default title bar
        self.setWindowFlags(Qt.FramelessWindowHint)
        QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))

        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Initialize conversion thread
        self.conversion_thread = None
        
        # Setup UI
        self.setup_ui()
        
    def progress_callback(self, data):
        """Callback function to increment progress by 10"""
        current = self.progress_bar.value()
        if current < 90:  # Don't go over 90 until conversion is complete
            self.progress_bar.setValue(current + 10)
        
    def apply_dark_theme(self):
        # Set dark palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(25, 25, 35))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 45))
        dark_palette.setColor(QPalette.AlternateBase, QColor(45, 45, 55))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(40, 40, 50))
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(50, 50, 60))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(79, 143, 240))
        dark_palette.setColor(QPalette.Highlight, QColor(79, 143, 240))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        
        self.setPalette(dark_palette)
        
        # Set style sheet for additional styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1A1A25;
            }
            QLabel {
                color: #FFFFFF;
                font-weight: 500;
            }
            QLineEdit {
                background-color: rgba(40, 40, 50, 0.9);
                color: #FFFFFF;
                border: 1px solid rgba(79, 143, 240, 0.3);
                padding: 8px;
                selection-background-color: #4F8FF0;
            }
            QLineEdit:focus {
                border: 1px solid rgba(79, 143, 240, 0.7);
            }
            QSpinBox {
                background-color: rgba(40, 40, 50, 0.9);
                color: #FFFFFF;
                border: 1px solid rgba(79, 143, 240, 0.3);
                padding: 8px;
            }
            QSpinBox:focus {
                border: 1px solid rgba(79, 143, 240, 0.7);
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: rgba(79, 143, 240, 0.3);
                border: none;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: rgba(79, 143, 240, 0.5);
            }
            QCheckBox {
                color: #FFFFFF;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid rgba(79, 143, 240, 0.5);
                background: rgba(40, 40, 50, 0.9);
            }
            QCheckBox::indicator:checked {
                background-color: #4F8FF0;
                border: 1px solid #4F8FF0;
            }
            QCheckBox::indicator:unchecked:hover {
                border: 1px solid rgba(79, 143, 240, 0.7);
            }
            QGroupBox {
                color: #FFFFFF;
                font-weight: bold;
                border: 1px solid rgba(79, 143, 240, 0.2);
                margin-top: 10px;
                padding-top: 15px;
                background-color: rgba(30, 30, 40, 0.7);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        
        # Create a square frame for the main content
        main_frame = SquareFrame()
        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setSpacing(20)
        frame_layout.setContentsMargins(20, 20, 20, 20)
                
        
        
        # Input parameters group
        input_group = QGroupBox("Conversion Settings")
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(15)
        
        # CSV Path
        csv_layout = QHBoxLayout()
        csv_label = QLabel("CSV File:")
        csv_label.setFont(QFont("Segoe UI", 10))
        self.csv_input = QLineEdit("./data/Employers_data.csv")
        
        # Create folder icon for browse button
        folder_pixmap = QPixmap(20, 20)
        folder_pixmap.fill(Qt.transparent)
        painter = QPainter(folder_pixmap)
        painter.setPen(QColor(255, 255, 255))
        painter.setBrush(QColor(255, 255, 255))
        # Draw a simple folder icon
        painter.drawRect(4, 6, 16, 12)
        painter.drawRect(2, 4, 6, 2)
        painter.end()
        
        csv_browse_btn = SquareButton("", "Browse", "Browse for CSV file")
        csv_browse_btn.clicked.connect(self.browse_csv)
        
        csv_layout.addWidget(csv_label)
        csv_layout.addWidget(self.csv_input)
        csv_layout.addWidget(csv_browse_btn)
        input_layout.addLayout(csv_layout)
        
        # Number of Analysis
        analysis_layout = QHBoxLayout()
        analysis_label = QLabel("Analysis Count:")
        analysis_label.setFont(QFont("Segoe UI", 10))
        self.analysis_spin = QSpinBox()
        self.analysis_spin.setRange(1, 1000)
        self.analysis_spin.setValue(50)
        self.analysis_spin.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        
        analysis_layout.addWidget(analysis_label)
        analysis_layout.addWidget(self.analysis_spin)
        analysis_layout.addStretch()
        input_layout.addLayout(analysis_layout)
        
        # Report Title
        report_title_layout = QHBoxLayout()
        report_title_label = QLabel("Report Title:")
        report_title_label.setFont(QFont("Segoe UI", 10))
        self.report_title_input = QLineEdit("Employers Data Analysis Report")
        
        report_title_layout.addWidget(report_title_label)
        report_title_layout.addWidget(self.report_title_input)
        input_layout.addLayout(report_title_layout)
        
        # Footer Text
        footer_layout = QHBoxLayout()
        footer_label = QLabel("Footer Text:")
        footer_label.setFont(QFont("Segoe UI", 10))
        self.footer_input = QLineEdit("Generated by Data Analysis Story Teller")
        
        footer_layout.addWidget(footer_label)
        footer_layout.addWidget(self.footer_input)
        input_layout.addLayout(footer_layout)
        
        # Output File
        output_layout = QHBoxLayout()
        output_label = QLabel("Output File:")
        output_label.setFont(QFont("Segoe UI", 10))
        self.output_input = QLineEdit("final.html")
        
        # Create save icon for browse button
        save_pixmap = QPixmap(20, 20)
        save_pixmap.fill(Qt.transparent)
        painter = QPainter(save_pixmap)
        painter.setPen(QColor(255, 255, 255))
        painter.setBrush(QColor(255, 255, 255))
        # Draw a simple save icon (floppy disk)
        painter.drawRect(6, 4, 12, 16)
        painter.drawRect(8, 6, 8, 4)
        painter.drawRect(10, 12, 4, 6)
        painter.end()
        
        output_browse_btn = SquareButton("", "Browse", "Select output location")
        output_browse_btn.clicked.connect(self.browse_output)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_input)
        output_layout.addWidget(output_browse_btn)
        input_layout.addLayout(output_layout)
        
        # Page Title
        page_title_layout = QHBoxLayout()
        page_title_label = QLabel("Page Title:")
        page_title_label.setFont(QFont("Segoe UI", 10))
        self.page_title_input = QLineEdit("Employers Dataset Report")
        
        page_title_layout.addWidget(page_title_label)
        page_title_layout.addWidget(self.page_title_input)
        input_layout.addLayout(page_title_layout)
        
        # Dark Theme Checkbox
        self.dark_theme_checkbox = QCheckBox("Use Dark Theme in Report")
        self.dark_theme_checkbox.setFont(QFont("Segoe UI", 10))
        input_layout.addWidget(self.dark_theme_checkbox)
        
        frame_layout.addWidget(input_group)
        
        # Progress Bar
        progress_label = QLabel("Conversion Progress:")
        progress_label.setFont(QFont("Segoe UI", 10))
        frame_layout.addWidget(progress_label)
        
        self.progress_bar = SquareProgressBar()
        self.progress_bar.setValue(0)
        frame_layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Create start icon (play triangle)
        start_pixmap = QPixmap(20, 20)
        start_pixmap.fill(Qt.transparent)
        painter = QPainter(start_pixmap)
        painter.setPen(QColor(255, 255, 255))
        painter.setBrush(QColor(255, 255, 255))
        # painter.drawPolygon([(5, 5), (5, 15), (15, 10)])
        painter.end()
        
        self.start_btn = SquareButton("", "Start", "Start conversion")
        self.start_btn.clicked.connect(self.start_conversion)
        
        # Create stop icon (square)
        stop_pixmap = QPixmap(20, 20)
        stop_pixmap.fill(Qt.transparent)
        painter = QPainter(stop_pixmap)
        painter.setPen(QColor(255, 255, 255))
        painter.setBrush(QColor(255, 255, 255))
        painter.drawRect(5, 5, 10, 10)
        painter.end()
        
        self.stop_btn = SquareButton("", "Stop", "Stop conversion")
        self.stop_btn.clicked.connect(self.stop_conversion)
        self.stop_btn.setEnabled(False)
        
        # Create exit icon (X)
        exit_pixmap = QPixmap(20, 20)
        exit_pixmap.fill(Qt.transparent)
        painter = QPainter(exit_pixmap)
        painter.setPen(QColor(255, 255, 255))
        painter.drawLine(5, 5, 15, 15)
        painter.drawLine(15, 5, 5, 15)
        painter.end()
        
        self.exit_btn = SquareButton("", "Exit", "Exit application")
        self.exit_btn.clicked.connect(self.close)
        # Style exit button differently
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(180, 70, 70, 0.9);
                color: white;
                border: 1px solid rgba(200, 90, 90, 0.3);
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(200, 90, 90, 0.9);
                border: 1px solid rgba(220, 110, 110, 0.9);
            }
            QPushButton:pressed {
                background-color: rgba(220, 110, 110, 0.9);
            }
        """)

        # Move button
        self.move_btn = SquareButton("", "Move", "Move application")
        self.move_btn.setToolTip("Hold and drag to move window")
     
        # Add mouse event handlers
        self.move_btn.installEventFilter(self)
        
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.exit_btn)
        button_layout.addWidget(self.move_btn)

        
        frame_layout.addLayout(button_layout)
        main_layout.addWidget(main_frame)
        

        
    def browse_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "", "CSV Files (*.csv)"
        )
        if file_path:
            self.csv_input.setText(file_path)
            
    def browse_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Output File", "", "HTML Files (*.html)"
        )
        if file_path:
            self.output_input.setText(file_path)
            
    def start_conversion(self):
        # Get all parameters from UI
        conversion_kwargs = {
            "csv_path": self.csv_input.text(),
            "number_of_analyses": self.analysis_spin.value(),
            "report_title": self.report_title_input.text(),
            "footer_text": self.footer_input.text(),
            "output_file": self.output_input.text(),
            "page_title": self.page_title_input.text(),
            "dark_theme": self.dark_theme_checkbox.isChecked(),
            "callback_func": self.progress_callback  # Add the callback function
        }
        
        # Validate required fields
        if not conversion_kwargs["csv_path"]:
            QMessageBox.warning(self, "Warning", "Please select a CSV file.")
            return
            
        # Disable start button and enable stop button
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Reset progress bar
        self.progress_bar.setValue(0)
        
        # Update status
        self.statusBar().showMessage("Converting data...")
        
        # Create and start conversion thread
        self.conversion_thread = ConversionThread(self.convert_dataset_to_report, conversion_kwargs)
        self.conversion_thread.conversion_finished.connect(self.conversion_finished)
        self.conversion_thread.start()
        
    def stop_conversion(self):
        if self.conversion_thread and self.conversion_thread.isRunning():
            self.conversion_thread.terminate()
            self.conversion_thread.wait()
            self.conversion_finished(False)
            
    def conversion_finished(self, success):
        # Set progress to 100% if successful
        if success:
            self.progress_bar.setValue(100)
            self.statusBar().showMessage("Conversion completed successfully!")
            QMessageBox.information(self, "Success", "Conversion completed successfully!")
        else:
            self.progress_bar.setValue(0)
            self.statusBar().showMessage("Conversion stopped or failed")
            QMessageBox.warning(self, "Stopped", "Conversion was stopped or failed.")
            
        # Reset buttons
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
    def eventFilter(self, source, event):
        if source == self.move_btn:
            if event.type() == event.MouseButtonPress and event.button() == Qt.LeftButton:
                self._drag_active = True
                self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
                self.move_btn.setCursor(Qt.ClosedHandCursor)
                return True
            elif event.type() == event.MouseMove and self._drag_active:
                self.move(event.globalPos() - self._drag_position)
                return True
            elif event.type() == event.MouseButtonRelease and event.button() == Qt.LeftButton:
                self._drag_active = False
                self.move_btn.setCursor(Qt.OpenHandCursor)
                return True
        return super().eventFilter(source, event)

