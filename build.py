import os
import shutil
import subprocess
import sys

print("Compilando...")

subprocess.run([
    sys.executable,
    "-m",
    "PyInstaller",
    "--clean",
    "--noconfirm",
    "--onefile",
    "--windowed",
    "--collect-all",
    "flet",
    "--collect-all",
    "flet_desktop",
    "--name",
    "TrendnetSSH",
    "app.py"
], check=True)

print("Preparando archivos junto al exe...")

os.makedirs("dist/logs", exist_ok=True)
os.makedirs("dist/screenshots", exist_ok=True)

if os.path.exists("switches.xlsx"):
    shutil.copy(
        "switches.xlsx",
        "dist/switches.xlsx"
    )

if os.path.exists("switches.db"):
    shutil.copy(
        "switches.db",
        "dist/switches.db"
    )

print("Listo.")