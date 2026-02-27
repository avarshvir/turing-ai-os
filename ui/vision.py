import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                             QWidget, QLabel, QTextBrowser, QPushButton, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.llm_engine import TuringLLMEngine

class AIWorker(QThread):
    token_received = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, engine, prompt):
        super().__init__()
        self.engine = engine
        self.prompt = prompt

    def run(self):
        for chunk in self.engine.stream_response(self.prompt):
            self.token_received.emit(chunk)
        self.finished.emit()

class TuringVision(QMainWindow):
    def __init__(self, target_path):
        super().__init__()
        self.target_path = target_path
        self.engine = TuringLLMEngine()
        self.init_ui()
        self.analyze_target()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(600, 500)
        
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.central_widget.setStyleSheet("""
            QWidget { background-color: rgba(255, 255, 255, 210); border-radius: 15px; border: 1px solid rgba(200, 200, 200, 150); }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 5)
        self.central_widget.setGraphicsEffect(shadow)

        target_name = os.path.basename(self.target_path)
        self.header = QLabel(f"Turing Vision: Analyzing '{target_name}'")
        self.header.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        self.header.setStyleSheet("background: transparent; color: #1a1a1a;")
        self.layout.addWidget(self.header)

        self.output_area = QTextBrowser()
        self.output_area.setFont(QFont("Inter", 12))
        self.output_area.setStyleSheet("""
            QTextBrowser { background: rgba(255, 255, 255, 100); border: 1px solid #ccc; border-radius: 8px; color: #333; padding: 10px; }
        """)
        self.layout.addWidget(self.output_area)

        self.close_btn = QPushButton("Close Vision")
        self.close_btn.setStyleSheet("""
            QPushButton { background-color: #0078D7; color: white; border-radius: 8px; padding: 10px; font-weight: bold; }
            QPushButton:hover { background-color: #005A9E; }
        """)
        self.close_btn.clicked.connect(self.close)
        self.layout.addWidget(self.close_btn)

    def analyze_target(self):
        # OS-Level Routing: Route to folder logic or file logic
        if os.path.isdir(self.target_path):
            self.analyze_folder()
        else:
            self.analyze_file()

    def analyze_folder(self):
        try:
            # Read folder contents (limit to 30 items to save AI context window)
            items = os.listdir(self.target_path)[:30]
            tree_structure = "\n".join([f"- {item}" for item in items])
            
            prompt = f"Look at this folder structure and explain what kind of project or directory this likely is:\n\n{tree_structure}"
            self.output_area.setText("<i>Scanning directory structure and querying local AI engine...</i><br><br>")
            self.start_worker(prompt)
        except Exception as e:
            self.output_area.setText(f"<b style='color:red;'>Folder Error:</b> {str(e)}")

    def analyze_file(self):
        try:
            with open(self.target_path, 'r', encoding='utf-8') as f:
                content = f.read(2000) 
            
            prompt = f"Please provide a concise summary and explain the purpose of the following file contents:\n\n{content}"
            self.output_area.setText("<i>Reading file contents and querying local AI engine...</i><br><br>")
            self.start_worker(prompt)
        except Exception as e:
            self.output_area.setText(f"<b style='color:red;'>File Error:</b> {str(e)}<br>This might not be a readable text file.")

    def start_worker(self, prompt):
        self.worker = AIWorker(self.engine, prompt)
        self.worker.token_received.connect(self.update_output)
        self.worker.start()

    def update_output(self, text_chunk):
        cursor = self.output_area.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(text_chunk)
        self.output_area.setTextCursor(cursor)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Error: No file or folder path provided.")
        sys.exit(1)
        
    app = QApplication(sys.argv)
    vision = TuringVision(sys.argv[1])
    vision.show()
    sys.exit(app.exec())