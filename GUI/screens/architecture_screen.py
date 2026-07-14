import shutil
import sqlite3
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
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.UPLOAD_FILE, size=16, color="#0B1D33"),
                                        ft.Text("Cargar backup .db", weight=ft.FontWeight.BOLD, color="#0B1D33"),
                                    ],
                                    spacing=8,
                                    tight=True,
                                ),
                                bgcolor="#C97A1B",
                                on_click=self._pick_db,
                            ),
                            ft.OutlinedButton(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.DOWNLOAD, size=16, color=INK),
                                        ft.Text("Descargar backup .db", color=INK),
                                    ],
                                    spacing=8,
                                    tight=True,
                                ),
                                on_click=self._save_backup_db,
                            ),
                        ],
                        spacing=8,
                        wrap=True,
                    ),
                ),
                panel(
                    ft.Icons.TABLE_CHART,
                    "Subir Excel",
                    "Importa datos desde .xlsx, .xls o .csv a switches.db",
                    None,
                    ft.Column(
                        [
                            ft.ElevatedButton(
                                content=ft.Row(
                                    [ft.Icon(ft.Icons.UPLOAD_FILE, size=16, color="#0B1D33"),
                                     ft.Text("Subir Excel/CSV de switches", weight=ft.FontWeight.BOLD, color="#0B1D33")],
                                    spacing=8, tight=True,
                                ),
                                bgcolor="#C97A1B",
                                on_click=self._pick_switch_excel,
                            ),
                            ft.ElevatedButton(
                                content=ft.Row(
                                    [ft.Icon(ft.Icons.UPLOAD_FILE, size=16, color="#0B1D33"),
                                     ft.Text("Subir Excel/CSV de camaras", weight=ft.FontWeight.BOLD, color="#0B1D33")],
                                    spacing=8, tight=True,
                                ),
                                bgcolor="#C97A1B",
                                on_click=self._pick_camera_excel,
                            ),
                        ],
                        spacing=8,
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
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["db", "sqlite", "sqlite3"],
        )
        self._on_db_selected(files)

    async def _save_backup_db(self, _):
        try:
            source = Path("switches.db")
            if not source.exists():
                self.feedback.value = "No existe switches.db para descargar"
                self.feedback.color = DANGER
                self.update()
                return

            default_name = f"switches_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            selected_path = await self._db_picker.save_file(
                dialog_title="Guardar backup de base de datos",
                file_name=default_name,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["db", "sqlite", "sqlite3"],
            )

            if not selected_path:
                return

            destination = Path(selected_path)
            if destination.suffix.lower() not in {".db", ".sqlite", ".sqlite3"}:
                destination = destination.with_suffix(".db")

            if destination.resolve() == source.resolve():
                self.feedback.value = "Selecciona un nombre de archivo distinto para el backup"
                self.feedback.color = DANGER
                self.update()
                return

            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

            self.feedback.value = f"Backup descargado en: {destination.name}"
            self.feedback.color = GREEN_700
            self.update()

        except Exception as ex:
            self.feedback.value = f"Error descargando backup .db: {ex}"
            self.feedback.color = DANGER
            self.update()

    async def _pick_switch_excel(self, _):
        await self._pick_excel_for_type("switch", "switches")

    async def _pick_camera_excel(self, _):
        await self._pick_excel_for_type("camara", "camaras")

    async def _pick_excel_for_type(self, tipo_default, etiqueta):
        files = await self._excel_picker.pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["xlsx", "xls", "csv"],
        )
        self._on_excel_selected(files, tipo_default, etiqueta)

    def _on_db_selected(self, files):
        try:
            if not files:
                return

            if not files[0].path:
                self.feedback.value = "Error: no se pudo leer la ruta del archivo seleccionado"
                self.feedback.color = DANGER
                self.update()
                return

            source = Path(files[0].path)
            target = Path("switches.db")

            if not source.exists():
                self.feedback.value = "Error: no se encontro el archivo seleccionado"
                self.feedback.color = DANGER
                self.update()
                return

            valid, message = self._validate_backup_db(source)
            if not valid:
                self.feedback.value = message
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

    def _validate_backup_db(self, source: Path):
        required_tables = {"switches", "ssh_command_library"}

        try:
            with sqlite3.connect(str(source)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = {row[0] for row in cursor.fetchall()}

                missing = sorted(required_tables - tables)
                if missing:
                    return False, f"El backup no es valido, faltan tablas: {', '.join(missing)}"

                cursor.execute("SELECT COUNT(*) FROM switches")
                total_devices = cursor.fetchone()[0]

            return True, f"Backup valido con {total_devices} devices"
        except sqlite3.Error as ex:
            return False, f"El archivo no parece una base SQLite valida: {ex}"

    def _on_excel_selected(self, files, tipo_default="switch", etiqueta="switches"):
        try:
            if not files:
                return

            file_path = Path(files[0].path)
            manager = ExcelManager("switches.db")
            manager.abrir()

            manager.importar_desde_archivo(str(file_path), tipo_default=tipo_default)

            self.feedback.value = f"Archivo importado para {etiqueta}: {file_path.name}"
            self.feedback.color = GREEN_700
            self._notify_change()
            self.update()

        except Exception as ex:
            self.feedback.value = f"Error importando archivo: {ex}"
            self.feedback.color = DANGER
            self.update()