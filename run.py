import os
import platform
import subprocess
import sys
from pathlib import Path

# Paths
venv_dir = Path("venv")
requirements = Path("requirements.txt")
reset_db = Path("reset_db.py")
main_script = Path("main.py")

# 1. Create virtual environment if it doesn't exist
if not venv_dir.exists():
    print("Creating virtual environment...")
    subprocess.check_call([sys.executable, "-m", "venv", str(venv_dir)])

# 2. Get the path to the Python executable inside the venv
if platform.system() == "Windows":
    python_exec = venv_dir / "Scripts" / "python.exe"
else:
    python_exec = venv_dir / "bin" / "python"

# 3. Install dependencies if requirements.txt exists
if requirements.exists():
    print("Installing dependencies from requirements.txt...")
    subprocess.check_call([str(python_exec), "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.check_call([str(python_exec), "-m", "pip", "install", "-r", str(requirements)])
else:
    print("requirements.txt not found, skipping installation.")

# 4. Run database setup
if reset_db.exists():
    print("Setting up database via reset_db.py...")
    subprocess.check_call([str(python_exec), str(reset_db)])
else:
    print("reset_db.py not found, skipping DB reset.")

# 5. Run main.py
print(f"Running {main_script}...")
subprocess.check_call([str(python_exec), str(main_script)])
