import threading

import flet as ft

from backend.controller import Controller
from modules.excel import ExcelManager
from GUI.widget.process_ssh_panel import ProcessSSHPanel
from GUI.widget.ssh_commands_panel import SSHCommandsPanel
from GUI.theme import (
    AMBER_400,
    AMBER_600,
    DANGER,
    GREEN_500,
    INK,
    NAVY_800,
    SLATE_400,
    card,
    section_title,
)


class ProcessAutomaticsScreen(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True)

        self._page = page
        self.controller = Controller()
        self._library_checkboxes = []

        self.default_commands = [
            "show interface",
            "show running-config",
            "show mac-address-table",
            "show vlan",
            "show spanning-tree",
        ]

        self.log_output = ft.TextField(
            multiline=True,
            read_only=True,
            min_lines=14,
            max_lines=22,
            expand=True,
            bgcolor=NAVY_800,
            color=GREEN_500,
            border_color=ft.Colors.with_opacity(0.10, "#FFFFFF"),
            focused_border_color=AMBER_600,
            cursor_color=AMBER_600,
            text_style=ft.TextStyle(font_family="Consolas", size=13),
            hint_text="Sin actividad todavia...",
            hint_style=ft.TextStyle(color=SLATE_400, font_family="Consolas"),
        )

        self.summary = card(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=GREEN_500, size=20),
                    ft.Text("", size=13, color=GREEN_500, expand=True, selectable=True),
                ],
                spacing=10,
            ),
            bgcolor=ft.Colors.with_opacity(0.10, GREEN_500),
            border_color=ft.Colors.with_opacity(0.30, GREEN_500),
        )
        self.summary.visible = False

        self.process_ssh_panel = ProcessSSHPanel(on_run=self._run_process)
        self.ssh_commands_panel = SSHCommandsPanel(
            on_add_command=self._add_command_to_library,
            on_reload_library=self._reload_command_library,
            on_run_commands=self._run_ssh_commands,
        )

        # Contenedor unico cuyo `content` se reemplaza por completo al cambiar
        # de tab. Esto evita depender de alternar `visible` en dos controles
        # que ya conviven en el arbol, lo cual en Flet 0.83+ (nuevo motor de
        # diffing) puede dejar sin renderizar un subarbol que nunca se monto
        # visible en el primer render.
        self.active_panel = ft.Container(content=self.process_ssh_panel)

        self.process_tabs = self._build_process_tabs()

        self.content = ft.Column(
            [
                self._build_header(),
                ft.Text(
                    "Ejecuta procesos automaticos y visualiza salida de consola en vivo",
                    size=13,
                    color=SLATE_400,
                ),
                self.process_tabs,
                self.active_panel,
                section_title(ft.Icons.TERMINAL, "Proceso"),
                self.log_output,
                section_title(ft.Icons.SUMMARIZE, "Resumen"),
                self.summary,
            ],
            spacing=12,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        self._ensure_default_command_library()
        self._load_command_library()

    @property
    def run_button(self):
        return self.process_ssh_panel.run_button

    @property
    def run_commands_button(self):
        return self.ssh_commands_panel.run_button

    @property
    def new_command_input(self):
        return self.ssh_commands_panel.new_command_input

    @property
    def library_container(self):
        return self.ssh_commands_panel.library_container

    @property
    def custom_commands_input(self):
        return self.ssh_commands_panel.custom_commands_input

    def _build_header(self):
        return ft.Row(
            [
                ft.Icon(ft.Icons.SETTINGS_SUGGEST, color=AMBER_400, size=26),
                ft.Text("Process Automatics", size=26, weight=ft.FontWeight.BOLD, color=INK),
            ],
            spacing=10,
        )

    def _build_process_tabs(self):
        return ft.Tabs(
            length=2,
            selected_index=0,
            animation_duration=180,
            on_change=self._on_process_tab_change,
            content=ft.Column(
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Proceso SSH"),
                            ft.Tab(label="SSH Commands"),
                        ]
                    )
                ]
            ),
        )

    def _on_process_tab_change(self, e):
        selected = e.control.selected_index

        if selected == 1:
            self._load_command_library()  # recarga justo al mostrar
            self.active_panel.content = self.ssh_commands_panel
        else:
            self.active_panel.content = self.process_ssh_panel

        self.active_panel.update()

    def _append_log(self, text: str):
        if text.startswith("Resumen final"):
            self.summary.visible = True
            self.summary.content.controls[1].value = text
        else:
            self.log_output.value += f"{text}\n"

        self._page.update()

    def _start_process_run(self, runner_fn):
        self.run_button.disabled = True
        self.run_commands_button.disabled = True
        self.log_output.value = ""
        self.summary.visible = False
        self.summary.content.controls[1].value = ""
        self._page.update()

        def runner():
            try:
                runner_fn()
            finally:
                self.run_button.disabled = False
                self.run_commands_button.disabled = False
                self._page.update()

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()

    def _run_process(self, _):
        self._start_process_run(
            lambda: self.controller.ejecutar_activacion_ssh(self._append_log)
        )

    def _ensure_default_command_library(self):
        db = ExcelManager("switches.db")
        db.abrir()

        try:
            existentes = db.obtener_comandos_ssh()
            if existentes:
                return

            for cmd in self.default_commands:
                try:
                    db.agregar_comando_ssh(cmd)
                except ValueError:
                    pass
        finally:
            db.cerrar()

    def _load_command_library(self):
        db = ExcelManager("switches.db")
        db.abrir()

        try:
            comandos = db.obtener_comandos_ssh()
        finally:
            db.cerrar()

        self._library_checkboxes = []
        controls = []

        if not comandos:
            controls.append(ft.Text("No hay comandos en la libreria.", color=SLATE_400, size=12))

        for item in comandos:
            checkbox = ft.Checkbox(
                label=item["comando"],
                value=False,
                label_style=ft.TextStyle(color=INK, size=12),
                active_color=AMBER_600,
                check_color="#0B1D33",
            )
            self._library_checkboxes.append((checkbox, item["comando"]))
            controls.append(checkbox)

        self.library_container.controls = controls

    def _reload_command_library(self, _):
        self._load_command_library()
        self.update()

    def _add_command_to_library(self, _):
        comando = (self.new_command_input.value or "").strip()
        if not comando:
            self._append_log("ERROR: Escribe un comando para agregar a la libreria")
            return

        db = ExcelManager("switches.db")
        db.abrir()

        try:
            db.agregar_comando_ssh(comando)
        except ValueError as ex:
            self._append_log(f"ERROR: {ex}")
        except Exception as ex:
            self._append_log(f"ERROR agregando comando: {ex}")
        else:
            self.new_command_input.value = ""
            self._append_log(f"OK: comando agregado a libreria -> {comando}")
        finally:
            db.cerrar()

        self._load_command_library()
        self.update()

    def _collect_selected_commands(self):
        comandos = []

        for checkbox, comando in self._library_checkboxes:
            if checkbox.value:
                comandos.append(comando)

        libres = [
            line.strip()
            for line in (self.custom_commands_input.value or "").splitlines()
            if line.strip()
        ]
        comandos.extend(libres)

        # Eliminar duplicados preservando orden.
        return list(dict.fromkeys(comandos))

    def _run_ssh_commands(self, _):
        comandos = self._collect_selected_commands()

        if not comandos:
            self.summary.visible = True
            self.summary.content.controls[0].name = ft.Icons.ERROR_OUTLINE
            self.summary.content.controls[0].color = DANGER
            self.summary.content.controls[1].color = DANGER
            self.summary.content.controls[1].value = "Debes seleccionar o escribir al menos un comando"
            self._page.update()
            return

        self.summary.content.controls[0].name = ft.Icons.CHECK_CIRCLE
        self.summary.content.controls[0].color = GREEN_500
        self.summary.content.controls[1].color = GREEN_500

        self._start_process_run(
            lambda: self.controller.ejecutar_ssh_commands(self._append_log, comandos)
        )