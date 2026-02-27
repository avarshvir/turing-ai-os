import os
import shutil

class FileOperations:
    def __init__(self):
        self.base_dir = os.path.expanduser("~") # Default to user's home directory

    def list_directory(self, path=""):
        """Returns a list of files in the requested directory."""
        target_path = os.path.join(self.base_dir, path)
        try:
            items = os.listdir(target_path)
            return f"Contents of {target_path}:\n" + "\n".join(items)
        except Exception as e:
            return f"[System Error] Cannot read directory: {e}"

    def read_file(self, file_path):
        """Reads the contents of a text file."""
        target_path = os.path.join(self.base_dir, file_path)
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                content = f.read(3000) # Limit to 3000 chars to save RAM
            return f"--- FILE CONTENTS ({target_path}) ---\n{content}"
        except Exception as e:
            return f"[System Error] Cannot read file: {e}"

    def write_file(self, file_path, content):
        """Creates or overwrites a file with new content."""
        target_path = os.path.join(self.base_dir, file_path)
        try:
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"[Success] File written to {target_path}"
        except Exception as e:
            return f"[System Error] Cannot write file: {e}"

# Test the module
if __name__ == "__main__":
    ops = FileOperations()
    print("Testing File Ops...")
    print(ops.list_directory("turing-os"))
