import os
import platform
import subprocess
import sys
from pathlib import Path

# 1. Define the virtual environment directory and main file
venv_dir = Path("venv")
requirements_file = Path("requirements.txt")
main_file = "main.py"  # Change this if your project's entry point is different

# 2. Create a virtual environment if it doesn't exist
if not venv_dir.exists():
    print("Creating virtual environment...")
    subprocess.check_call([sys.executable, "-m", "venv", str(venv_dir)])

# 3. Determine the path to the virtual environment's Python executable
system = platform.system()
if system == "Windows":
    python_exec = venv_dir / "Scripts" / "python"
else:
    python_exec = venv_dir / "bin" / "python"

# 4. Install dependencies from requirements.txt
print("Installing dependencies...")
subprocess.check_call([str(python_exec), "-m", "pip", "install", "-r", str(requirements_file)])

# 5. Run the main Python application
print(f"Starting project with {main_file}...")
subprocess.check_call([str(python_exec), main_file])
