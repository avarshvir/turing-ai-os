import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                             QWidget, QLineEdit, QTextBrowser, QGraphicsDropShadowEffect)
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

class TuringSpotlight(QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = TuringLLMEngine()
        self.init_ui()

    def init_ui(self):
        # IMMUNITY FLAG: BypassWindowManagerHint protects it from the Top-Left rule
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.BypassWindowManagerHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Center the window on the screen (Top-Center)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry((screen.width() - 800) // 2, (screen.height() - 400) // 4, 800, 80)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.central_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 180); 
                border-radius: 20px;
                border: 1px solid rgba(200, 200, 200, 150);
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 10)
        self.central_widget.setGraphicsEffect(shadow)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ask Turing or type a command...")
        self.search_input.setFont(QFont("Inter", 18))
        self.search_input.setStyleSheet("background: transparent; border: none; color: #1a1a1a; padding: 10px;")
        self.search_input.returnPressed.connect(self.process_query)
        self.layout.addWidget(self.search_input)

        self.output_area = QTextBrowser()
        self.output_area.setFont(QFont("Inter", 14))
        self.output_area.setStyleSheet("background: transparent; border: none; color: #333333; margin-top: 10px;")
        self.output_area.hide()
        self.layout.addWidget(self.output_area)

    def process_query(self):
        prompt = self.search_input.text().strip()
        if not prompt: return
        if prompt.lower() in ["exit", "quit", "close"]: QApplication.quit()

        self.search_input.setReadOnly(True)
        self.output_area.show()
        self.output_area.clear()
        self.resize(800, 400) 

        self.worker = AIWorker(self.engine, prompt)
        self.worker.token_received.connect(self.update_output)
        self.worker.finished.connect(self.generation_complete)
        self.worker.start()

    def update_output(self, text_chunk):
        cursor = self.output_area.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(text_chunk)
        self.output_area.setTextCursor(cursor)

    def generation_complete(self):
        self.search_input.setReadOnly(False)
        self.search_input.clear()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    spotlight = TuringSpotlight()
    spotlight.show()
    sys.exit(app.exec())
