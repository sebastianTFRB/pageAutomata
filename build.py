import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

print("Compilando...")


def _on_rm_error(func, path, exc_info):
    try:
        os.chmod(path, 0o777)
        func(path)
    except Exception:
        pass


def _safe_rmtree(path: Path):
    if not path.exists():
        return

    for _ in range(3):
        try:
            shutil.rmtree(path, onerror=_on_rm_error)
            return
        except PermissionError:
            time.sleep(0.7)


def _safe_remove(path: Path):
    if not path.exists():
        return
    try:
        path.unlink()
    except PermissionError:
        os.chmod(path, 0o777)
        path.unlink(missing_ok=True)


for target in [Path("build"), Path("dist")]:
    _safe_rmtree(target)

_safe_remove(Path("TrendnetSSH.spec"))

cmd = [
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
    "--icon",
    "assets/app_icon.ico",
    "--name",
    "TrendnetSSH",
    "app.py"
]

for intento in (1, 2):
    try:
        subprocess.run(cmd, check=True)
        break
    except subprocess.CalledProcessError:
        if intento == 2:
            raise
        print("Reintentando compilacion por bloqueo temporal de archivos...")
        time.sleep(1.0)

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

# Copia navegadores de Playwright para que el EXE pueda abrir Chromium.
ms_playwright = Path.home() / "AppData" / "Local" / "ms-playwright"
dist_playwright = Path("dist") / "ms-playwright"

if ms_playwright.exists():
    if dist_playwright.exists():
        shutil.rmtree(dist_playwright)
    shutil.copytree(ms_playwright, dist_playwright)
    print(f"Playwright browsers copiados en: {dist_playwright}")
else:
    print("ADVERTENCIA: No se encontro ms-playwright para copiar navegadores")

print("Listo.")