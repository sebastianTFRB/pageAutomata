import os
import shutil
import subprocess

print("Compilando...")

subprocess.run([
    "pyinstaller",
    "--clean",
    "--noconfirm",
    "--windowed",
    "--name",
    "TrendnetSSH",
    "app.py"
])

print("Copiando archivos...")

os.makedirs("dist/TrendnetSSH/logs", exist_ok=True)
os.makedirs("dist/TrendnetSSH/screenshots", exist_ok=True)

if os.path.exists("switches.xlsx"):
    shutil.copy(
        "switches.xlsx",
        "dist/TrendnetSSH/switches.xlsx"
    )

print("Listo.")