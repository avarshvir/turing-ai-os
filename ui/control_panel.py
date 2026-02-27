import sys
import os
import json
import shutil
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QLabel, QPushButton, QComboBox, QSlider, QLineEdit, QGraphicsDropShadowEffect, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont

class ModelPullWorker(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, model_name):
        super().__init__()
        self.model_name = model_name

    def run(self):
        try:
            self.progress_signal.emit(f"Pulling {self.model_name}...")
            process = subprocess.Popen(['ollama', 'pull', self.model_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            process.communicate()
            if process.returncode == 0:
                self.finished_signal.emit(True, f"Successfully installed {self.model_name}!")
            else:
                self.finished_signal.emit(False, "Error pulling model.")
        except Exception as e:
            self.finished_signal.emit(False, str(e))

class TuringControlPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core", "config.json")
        self.memory_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory", "chroma_data")
        self.config_data = self.load_config()
        self.init_ui()
        self.refresh_installed_models()

    def load_config(self):
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except:
            return {"model": {"active_llm": "qwen2.5:1.5b", "temperature": 0.3}}

    def refresh_installed_models(self):
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            models = []
            for line in result.stdout.split('\n')[1:]:
                if line: models.append(line.split()[0])
            
            self.model_dropdown.clear()
            if models:
                self.model_dropdown.addItems(models)
                if self.config_data["model"].get("active_llm") in models:
                    self.model_dropdown.setCurrentText(self.config_data["model"]["active_llm"])
        except:
            self.model_dropdown.addItems(["qwen2.5:1.5b"])

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(550, 550)
        
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(30, 30, 30, 30)

        self.central_widget.setStyleSheet("""
            QWidget { background-color: rgba(255, 255, 255, 220); border-radius: 15px; border: 1px solid rgba(200, 200, 200, 150); }
            QLabel { background: transparent; border: none; color: #1a1a1a; }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        self.central_widget.setGraphicsEffect(shadow)

        title = QLabel("Turing AI Control Panel")
        title.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)

        # MODEL SELECTION & DELETION
        self.layout.addSpacing(15)
        self.layout.addWidget(QLabel("Active Neural Engine (LLM):"))
        
        model_row = QHBoxLayout()
        self.model_dropdown = QComboBox()
        self.model_dropdown.setStyleSheet("QComboBox { background: white; border: 1px solid #ccc; padding: 5px; }")
        model_row.addWidget(self.model_dropdown)

        self.delete_btn = QPushButton("Delete Model")
        self.delete_btn.setStyleSheet("background-color: #dc3545; color: white; padding: 5px 10px; border-radius: 5px;")
        self.delete_btn.clicked.connect(self.delete_model)
        model_row.addWidget(self.delete_btn)
        self.layout.addLayout(model_row)

        # DOWNLOAD NEW MODEL
        self.layout.addSpacing(15)
        self.layout.addWidget(QLabel("Install New Model:"))
        install_layout = QHBoxLayout()
        self.new_model_input = QLineEdit()
        self.new_model_input.setPlaceholderText("e.g., mistral")
        self.new_model_input.setStyleSheet("QLineEdit { background: white; border: 1px solid #ccc; padding: 5px; }")
        install_layout.addWidget(self.new_model_input)

        self.install_btn = QPushButton("Pull")
        self.install_btn.setStyleSheet("background-color: #28a745; color: white; padding: 5px 10px; border-radius: 5px;")
        self.install_btn.clicked.connect(self.pull_model)
        install_layout.addWidget(self.install_btn)
        self.layout.addLayout(install_layout)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #0078D7; font-size: 11px;")
        self.layout.addWidget(self.status_label)

        # SYSTEM MEMORY
        self.layout.addSpacing(10)
        self.wipe_memory_btn = QPushButton("Wipe AI Vector Memory (ChromaDB)")
        self.wipe_memory_btn.setStyleSheet("background-color: #ff9800; color: white; padding: 8px; border-radius: 5px; font-weight: bold;")
        self.wipe_memory_btn.clicked.connect(self.wipe_memory)
        self.layout.addWidget(self.wipe_memory_btn)

        # TEMPERATURE
        self.layout.addSpacing(15)
        self.layout.addWidget(QLabel("System Temperature (Precision vs. Creativity):"))
        self.temp_slider = QSlider(Qt.Orientation.Horizontal)
        self.temp_slider.setMinimum(0)
        self.temp_slider.setMaximum(100)
        self.temp_slider.setValue(int(self.config_data["model"].get("temperature", 0.3) * 100))
        self.layout.addWidget(self.temp_slider)

        # BUTTONS
        self.layout.addStretch()
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("background-color: #e0e0e0; padding: 10px; border-radius: 8px;")
        btn_layout.addWidget(close_btn)

        save_btn = QPushButton("Save Configuration")
        save_btn.clicked.connect(self.save_config)
        save_btn.setStyleSheet("background-color: #0078D7; padding: 10px; border-radius: 8px; color: white; font-weight: bold;")
        btn_layout.addWidget(save_btn)
        self.layout.addLayout(btn_layout)

    def wipe_memory(self):
        reply = QMessageBox.question(self, 'Confirm Wipe', 'Delete all AI long-term memory?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if os.path.exists(self.memory_path):
                    shutil.rmtree(self.memory_path)
                QMessageBox.information(self, "Success", "Vector memory wiped. It will be recreated on next boot.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to wipe memory: {e}")

    def delete_model(self):
        model = self.model_dropdown.currentText()
        if not model: return
        reply = QMessageBox.question(self, 'Confirm Delete', f'Delete the {model} model from your SSD?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.status_label.setText(f"Deleting {model}...")
            subprocess.run(['ollama', 'rm', model])
            self.refresh_installed_models()
            self.status_label.setText(f"{model} deleted.")

    def pull_model(self):
        model_name = self.new_model_input.text().strip()
        if not model_name: return
        self.install_btn.setDisabled(True)
        self.worker = ModelPullWorker(model_name)
        self.worker.progress_signal.connect(lambda msg: self.status_label.setText(msg))
        self.worker.finished_signal.connect(self.on_pull_finished)
        self.worker.start()

    def on_pull_finished(self, success, message):
        self.install_btn.setDisabled(False)
        self.status_label.setText(message)
        if success:
            self.refresh_installed_models()
            self.new_model_input.clear()

    def save_config(self):
        self.config_data["model"]["active_llm"] = self.model_dropdown.currentText()
        self.config_data["model"]["temperature"] = self.temp_slider.value() / 100.0
        with open(self.config_path, "w") as f:
            json.dump(self.config_data, f, indent=4)
        QMessageBox.information(self, "Updated", "Configuration Saved.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    panel = TuringControlPanel()
    panel.show()
    sys.exit(app.exec())