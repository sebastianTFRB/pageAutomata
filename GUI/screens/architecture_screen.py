import shutil
from datetime import datetime
from pathlib import Path

import flet as ft

from modules.excel import ExcelManager
from GUI.theme import AMBER_400, DANGER, GREEN_700, INK, SLATE_400, card, section_title


class ArchitectureScreen(ft.Container):
    def __init__(self, page: ft.Page, on_data_changed=None):
        super().__init__(expand=True)

        self._page = page
        self._on_data_changed = on_data_changed

        self.feedback = ft.Text("", size=12, color=SLATE_400)

        self._db_picker = ft.FilePicker()
        self._excel_picker = ft.FilePicker()

        self._page.services.append(self._db_picker)
        self._page.services.append(self._excel_picker)

        def panel(icon, title, description, extra, button):
            return card(
                content=ft.Column(
                    [
                        section_title(icon, title),
                        ft.Text(description, size=12, color=SLATE_400),
                        *([ft.Text(extra, size=11, color=SLATE_400)] if extra else []),
                        button,
                    ],
                    spacing=8,
                ),
            )

        self.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.ACCOUNT_TREE, color=AMBER_400, size=26),
                        ft.Text("Architecture", size=26, weight=ft.FontWeight.BOLD, color=INK),
                    ],
                    spacing=10,
                ),
                ft.Text(
                    "Herramientas de arquitectura, backup y carga de datos",
                    size=13,
                    color=SLATE_400,
                ),
                panel(
                    ft.Icons.STORAGE,
                    "Base de datos",
                    "Boton placeholder (sin funcion por ahora)",
                    None,
                    ft.OutlinedButton(
                        content=ft.Row(
                            [ft.Icon(ft.Icons.VISIBILITY, size=16, color=AMBER_400), ft.Text("Ver base de datos", color=INK)],
                            spacing=8, tight=True,
                        ),
                        on_click=self._view_db_placeholder,
                    ),
                ),
                panel(
                    ft.Icons.BACKUP,
                    "Backup",
                    "Carga un archivo .db para reemplazar la base actual",
                    "Puedes arrastrar si tu entorno lo soporta o usar el selector.",
                    ft.ElevatedButton(
                        content=ft.Row(
                            [ft.Icon(ft.Icons.UPLOAD_FILE, size=16, color="#0B1D33"),
                             ft.Text("Cargar backup .db", weight=ft.FontWeight.BOLD, color="#0B1D33")],
                            spacing=8, tight=True,
                        ),
                        bgcolor="#C97A1B",
                        on_click=self._pick_db,
                    ),
                ),
                panel(
                    ft.Icons.TABLE_CHART,
                    "Subir Excel",
                    "Importa datos desde .xlsx, .xls o .csv a switches.db",
                    None,
                    ft.ElevatedButton(
                        content=ft.Row(
                            [ft.Icon(ft.Icons.UPLOAD_FILE, size=16, color="#0B1D33"),
                             ft.Text("Subir Excel/CSV", weight=ft.FontWeight.BOLD, color="#0B1D33")],
                            spacing=8, tight=True,
                        ),
                        bgcolor="#C97A1B",
                        on_click=self._pick_excel,
                    ),
                ),
                self.feedback,
            ],
            spacing=12,
            expand=True,
        )

    def _notify_change(self):
        if self._on_data_changed:
            self._on_data_changed()

    def _view_db_placeholder(self, _):
        self.feedback.value = "Ver base de datos: pendiente de implementacion"
        self.feedback.color = SLATE_400
        self.update()

    async def _pick_db(self, _):
        files = await self._db_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["db", "sqlite", "sqlite3"],
        )
        self._on_db_selected(files)

    async def _pick_excel(self, _):
        files = await self._excel_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["xlsx", "xls", "csv"],
        )
        self._on_excel_selected(files)

    def _on_db_selected(self, files):
        try:
            if not files:
                return

            source = Path(files[0].path)
            target = Path("switches.db")

            if not source.exists():
                self.feedback.value = "Error: no se encontro el archivo seleccionado"
                self.feedback.color = DANGER
                self.update()
                return

            if target.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = target.with_name(f"switches_before_import_{timestamp}.db")
                shutil.copy2(target, backup_name)

            shutil.copy2(source, target)

            self.feedback.value = f"Backup cargado: {source.name}"
            self.feedback.color = GREEN_700
            self._notify_change()
            self.update()

        except Exception as ex:
            self.feedback.value = f"Error cargando backup .db: {ex}"
            self.feedback.color = DANGER
            self.update()

    def _on_excel_selected(self, files):
        try:
            if not files:
                return

            file_path = Path(files[0].path)
            manager = ExcelManager("switches.db")
            manager.abrir()

            if file_path.suffix.lower() == ".csv":
                manager.importar_desde_csv(str(file_path))
            else:
                manager.importar_desde_excel(str(file_path))

            self.feedback.value = f"Archivo importado: {file_path.name}"
            self.feedback.color = GREEN_700
            self._notify_change()
            self.update()

        except Exception as ex:
            self.feedback.value = f"Error importando archivo: {ex}"
            self.feedback.color = DANGER
            self.update()