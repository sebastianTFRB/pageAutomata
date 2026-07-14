import os
import sys
from pathlib import Path

def _runtime_base_dir() -> Path:
	if getattr(sys, "frozen", False):
		return Path(sys.executable).resolve().parent
	return Path(__file__).resolve().parent


runtime_dir = _runtime_base_dir()

# Garantiza rutas relativas consistentes (switches.db, logs, backups) en modo EXE.
os.chdir(runtime_dir)

# Debe configurarse antes de importar modulos que usan Playwright.
bundled_browsers = runtime_dir / "ms-playwright"
if bundled_browsers.exists():
	os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(bundled_browsers)
else:
	local_browsers = Path.home() / "AppData" / "Local" / "ms-playwright"
	if local_browsers.exists():
		os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(local_browsers)

from GUI.main_window import main

import flet as ft

ft.app(target=main)