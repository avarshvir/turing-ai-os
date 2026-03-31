<div align="center">

# 🧠 Turing AI OS
**The AI-Native Desktop Experience built on KDE Neon**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blueviolet.svg)](https://www.python.org/)
[![UI](https://img.shields.io/badge/UI-PyQt6-green.svg)](https://pypi.org/project/PyQt6/)
[![AI Engine](https://img.shields.io/badge/AI%20Engine-Ollama-orange.svg)](https://ollama.com/)
[![Default Model](https://img.shields.io/badge/Model-Qwen%202.5-red.svg)](https://qwenlm.github.io/)

Turing AI OS is a customized, intelligent layer built on top of the **KDE Neon** Linux distribution. It utilizes **Ollama** as a local, privacy-first AI backend and deeply integrates a suite of intelligent tools right into your desktop workflow.

</div>

---

## ✨ Key Features

Turing AI OS seamlessly weaves artificial intelligence into your daily tasks through a set of beautifully crafted, glassmorphism-styled PyQt6 applications:

*   **💬 Turing Sidebar** (`ui/sidebar.py`)
    A persistent, translucent AI assistant that lives on the edge of your screen. It features a persistent memory system (SSD-backed) so Turing remembers previous interactions even after a reboot.
*   **🔍 Spotlight Search** (`ui/spotlight.py`)
    A lightning-fast, floating command palette. Press a shortcut, type a natural language query or command, and get instant streaming answers from the local LLM.
*   **💻 Turing Shell** (`ui/turing_shell.py`)
    A natural-language terminal built with `rich`. Don't know how to do something in Ubuntu/KDE? Just ask in plain English. Turing Shell translates your intent into precise Bash commands, explains them to you, and executes them upon your confirmation.
*   **👁️ Turing Vision** (`ui/vision.py`)
    Context-aware AI analysis. Point it at a file, a script, or an entire project directory, and Turing Vision will read the contents, analyze the structure, and provide a comprehensive explanation of what it does.
*   **🎛️ AI Control Panel** (`ui/control_panel.py`)
    Your central hub for AI settings. Easily swap out local logic engines (models), download new models from Ollama, wipe long-term vector memory, and tweak the system's generation temperature.

## 🏗️ Architecture & Core Components

Turing AI OS is specifically designed for speed, privacy, and low resource utilization (optimized to run fast even on standard CPUs like an i3), utilizing local execution for all AI tasks.

*   **`core/llm_engine.py`**: The bridge to the Ollama backend. It uses `langchain-ollama` to interface with the local server, injecting the Turing OS System Persona into every interaction and handling token streaming for lag-free UI experiences.
*   **`memory/chroma_db_manager.py`**: A local Vector Database using `chromadb`. All Sidebar conversations are embedded and saved to SSD. When you talk to Turing, it silently searches this memory bank to construct augmented prompts.
*   **`skills/`**: The system's action layer.
    *   `file_ops.py`: Allows the AI to read your directories and files.
    *   `shell_ops.py`: Specialized system prompt that forces the LLM to output valid bash commands without markdown.
*   **`ui/`**: The graphical layer. All components are built with PyQt6, utilizing frameless windows, translucent backgrounds, and drop shadows to match the custom KDE Neon aesthetics.

## 🚀 Installation & Setup

### Prerequisites
*   **OS**: KDE Neon (or any modern Linux distribution)
*   **Python**: 3.12 or newer
*   **Ollama**: Installed and running in the background ([Download Ollama](https://ollama.com/download))

### Step-by-Step Guide

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/turing-ai-os.git
   cd turing-ai-os
   ```

2. **Install Python Dependencies**
   It's recommended to use a virtual environment.
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Ollama Service**
   Ensure your local AI engine is running:
   ```bash
   ollama serve
   ```

4. **Pull the Default Neural Engine**
   Turing AI OS defaults to `qwen2.5:1.5b` for extreme speed and efficiency:
   ```bash
   ollama pull qwen2.5:1.5b
   ```

5. **Launch the Utilities**
   You can map these Python scripts to global KDE keyboard shortcuts to launch them instantly:
   ```bash
   python ui/sidebar.py         # Launch the sliding assistant
   python ui/spotlight.py       # Launch the quick command palette
   python ui/control_panel.py   # Edit settings and download models
   python ui/turing_shell.py    # Start the Natural Language Terminal
   ```
   *To use Turing Vision, pass a file or folder path as an argument:*
   ```bash
   python ui/vision.py /path/to/my/code/
   ```

## ⚙️ Configuration

The system's behavior is controlled by `core/config.json`. You can edit this directly or use the graphical **AI Control Panel**.

```json
{
    "model": {
        "active_llm": "qwen2.5:1.5b",
        "temperature": 0.3,
        "max_ram_usage_gb": 2.0
    },
    "memory": {
        "enabled": true,
        "vector_db_path": "./memory/chroma_db"
    },
    ...
}
```

## 📄 License
Turing AI OS is released under the [Apache License 2.0](LICENSE).
