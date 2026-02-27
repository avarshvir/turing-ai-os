import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.llm_engine import TuringLLMEngine

class ShellAgent:
    def __init__(self):
        self.engine = TuringLLMEngine()

    def translate_to_bash(self, natural_language_query: str) -> str:
        """Translates English to a precise Ubuntu/KDE bash command."""
        prompt = (
            "You are a strict Linux command line translator for Ubuntu/KDE Neon. "
            f"Translate the following user intent into a single, exact bash command: '{natural_language_query}'\n"
            "Respond ONLY with the command itself. Do not include markdown formatting, backticks, or any explanation."
        )
        
        # We use generate_response for a fast, one-shot translation
        command = self.engine.generate_response(prompt).strip()
        
        # Clean up in case the LLM disobeys and adds markdown
        if command.startswith("```bash"):
            command = command.replace("```bash", "").replace("```", "").strip()
        elif command.startswith("```"):
            command = command.replace("```", "").strip()
            
        return command