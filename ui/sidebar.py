import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QLineEdit, QTextBrowser, QPushButton, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.llm_engine import TuringLLMEngine
from memory.chroma_db_manager import TuringMemory
from skills.file_ops import FileOperations

class AIWorker(QThread):
    token_received = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, engine, memory, session_id, prompt):
        super().__init__()
        self.engine = engine
        self.memory = memory
        self.session_id = session_id
        self.prompt = prompt
        self.full_response = ""

    def run(self):
        context = self.memory.retrieve_context(self.session_id, self.prompt)

        # STRICT Memory Formatting so the AI doesn't get confused
        augmented_prompt = self.prompt
        if context:
            augmented_prompt = (
                f"BACKGROUND MEMORY (Do not mention this unless relevant):\n"
                f"<memory>\n{context}\n</memory>\n\n"
                f"USER'S CURRENT MESSAGE: {self.prompt}"
            )

        for chunk in self.engine.stream_response(augmented_prompt):
            self.full_response += chunk
            self.token_received.emit(chunk)

        self.memory.save_memory(self.session_id, "user", self.prompt)
        self.memory.save_memory(self.session_id, "turing", self.full_response)

        self.finished.emit()

class TuringSidebar(QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = TuringLLMEngine()
        self.memory = TuringMemory()
        self.session_id = "default_user_session" # Active chat session
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.BypassWindowManagerHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        screen = QApplication.primaryScreen().geometry()
        sidebar_width = 350
        self.setGeometry(0, 0, sidebar_width, screen.height())

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(15, 40, 15, 20) 

        self.central_widget.setStyleSheet("""
            QWidget { background-color: rgba(255, 255, 255, 190); border-right: 1px solid rgba(200, 200, 200, 150); }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(5, 0)
        self.central_widget.setGraphicsEffect(shadow)

        self.chat_history = QTextBrowser()
        self.chat_history.setFont(QFont("Inter", 12))
        self.chat_history.setStyleSheet("background: transparent; border: none; color: #2b2b2b;")
        self.chat_history.append("<b>Turing OS:</b> Core systems online. My memory modules are active.")
        self.layout.addWidget(self.chat_history)

        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type a message...")
        self.chat_input.setFont(QFont("Inter", 12))
        self.chat_input.setStyleSheet("""
            QLineEdit { background-color: rgba(255, 255, 255, 150); border: 1px solid rgba(200, 200, 200, 200); border-radius: 10px; padding: 10px; color: #1a1a1a; }
        """)
        self.chat_input.returnPressed.connect(self.process_query)
        input_layout.addWidget(self.chat_input)

        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton { background-color: rgba(0, 120, 215, 200); color: white; border-radius: 10px; padding: 10px; font-weight: bold; }
            QPushButton:hover { background-color: rgba(0, 120, 215, 255); }
        """)
        self.send_button.clicked.connect(self.process_query)
        input_layout.addWidget(self.send_button)

        self.layout.addLayout(input_layout)

    def process_query(self):
        user_text = self.chat_input.text().strip()
        if not user_text: return
        if user_text.lower() in ["exit", "quit", "close"]: QApplication.quit()

        self.chat_history.append(f"<br><b>User:</b> {user_text}")
        self.chat_history.append("<b>Turing:</b> ")
        self.chat_input.clear()
        self.chat_input.setReadOnly(True)
        self.send_button.setDisabled(True)

        from skills.file_ops import FileOperations
        file_ops = FileOperations()

        system_injection = ""

        # NATURAL LANGUAGE PARSING
        lower_text = user_text.lower()

        if "what files" in lower_text or "list" in lower_text:
            # Try to extract a folder name, default to home if none found
            path = ""
            if "turing-os" in lower_text:
                path = "turing-os"

            dir_contents = file_ops.list_directory(path)

            # STRICT SYSTEM PROMPT INJECTION to prevent hallucination
            system_injection = (
                f"\n\n[SYSTEM OVERRIDE]: You are the Turing AI OS. You HAVE successfully scanned the user's hard drive. "
                f"Here is the raw data from the '{path}' directory:\n"
                f"```\n{dir_contents}\n```\n"
                f"INSTRUCTION: Describe these files to the user as if you just looked at them."
            )

        # Combine the user's text with the secret system injection
        final_prompt = user_text + system_injection

        self.worker = AIWorker(self.engine, self.memory, self.session_id, final_prompt)
        self.worker.token_received.connect(self.update_output)
        self.worker.finished.connect(self.generation_complete)
        self.worker.start()

    def update_output(self, text_chunk):
        cursor = self.chat_history.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(text_chunk)
        self.chat_history.setTextCursor(cursor)

    def generation_complete(self):
        self.chat_input.setReadOnly(False)
        self.send_button.setDisabled(False)
        self.chat_input.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    sidebar = TuringSidebar()
    sidebar.show()
    sys.exit(app.exec())
