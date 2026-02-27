import os
import sys
import json
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

class TuringLLMEngine:
    def __init__(self):
        """
        Initializes the connection to the local Ollama instance.
        Reads model settings dynamically from config.json.
        """
        # Dynamically locate config.json in the same directory as this script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "config.json")
        
        try:
            with open(config_path, "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"CRITICAL: Configuration file not found at {config_path}")
            sys.exit(1)
        except json.JSONDecodeError:
            print("CRITICAL: Invalid JSON format in config.json")
            sys.exit(1)

        # Extract settings from config
        self.model_name = self.config["model"]["active_llm"]
        self.temperature = self.config["model"]["temperature"]
        
        try:
            # Connect to the local Ollama background service
            self.llm = ChatOllama(
                model=self.model_name,
                temperature=self.temperature,
                base_url="http://localhost:11434"
            )
        except Exception as e:
            print(f"CRITICAL: Failed to bind to Ollama engine. {e}")
            sys.exit(1)

        # The System Prompt defines the OS persona
        self.system_prompt = SystemMessage(
            content=(
                "You are Turing, the core intelligence layer of Turing AI OS. "
                "You are precise, helpful, and highly technical. "
                "You do not use fluff. You run locally, prioritizing user privacy and system efficiency."
            )
        )

    def generate_response(self, prompt: str) -> str:
        """
        Sends a single query to the AI and returns the complete text.
        Used for background OS tasks and one-shot commands.
        """
        messages = [
            self.system_prompt,
            HumanMessage(content=prompt)
        ]
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"[System Error] Failed to compute response: {str(e)}"

    def stream_response(self, prompt: str):
        """
        Streams the response token-by-token.
        This is critical for our PyQt6 GUI so the user doesn't feel lag
        while the i3 CPU generates the answer.
        """
        messages = [
            self.system_prompt,
            HumanMessage(content=prompt)
        ]
        try:
            for chunk in self.llm.stream(messages):
                yield chunk.content
        except Exception as e:
            yield f"[System Error] {str(e)}"


# ==========================================
# BOOTSTRAP TEST
# ==========================================
if __name__ == "__main__":
    print("Initializing Turing Core AI Bridge from Config...")
    engine = TuringLLMEngine()
    
    print(f"Successfully loaded model: {engine.model_name}")
    test_prompt = "Hello. What is your role in this operating system?"
    print(f"\nUser: {test_prompt}")
    print("Turing (Streaming): ", end="", flush=True)
    
    # Test the streaming capability exactly how our GUI will use it
    for text_chunk in engine.stream_response(test_prompt):
        print(text_chunk, end="", flush=True)
    print("\n\n[Bridge Test Complete]")