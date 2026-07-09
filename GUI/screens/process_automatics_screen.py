import threading

import flet as ft

from backend.controller import Controller
from GUI.theme import (
    AMBER_400,
    AMBER_600,
    GREEN_500,
    GREEN_700,
    INK,
    NAVY_700,
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

        self.run_button = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.PLAY_ARROW, color="#0B1D33", size=18),
                    ft.Text("Iniciar activacion SSH", weight=ft.FontWeight.BOLD, color="#0B1D33"),
                ],
                spacing=8,
                tight=True,
            ),
            bgcolor=AMBER_600,
            on_click=self._run_process,
        )

        self.ssh_actions = card(
            content=ft.Column(
                [
                    section_title(ft.Icons.KEY, "Acciones de activar SSH"),
                    ft.Text(
                        "Esta opcion ejecuta la automatizacion actual de activacion SSH.",
                        size=12,
                        color=SLATE_400,
                    ),
                    self.run_button,
                ],
                spacing=10,
            ),
        )
        self.ssh_actions.visible = False

        self.toggle_button = ft.OutlinedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.TERMINAL, size=16, color=AMBER_400),
                    ft.Text("Activar SSH", color=INK),
                ],
                spacing=8,
                tight=True,
            ),
            on_click=self._toggle_ssh_actions,
            style=ft.ButtonStyle(side=ft.BorderSide(1, AMBER_600)),
        )

        self.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.SETTINGS_SUGGEST, color=AMBER_400, size=26),
                        ft.Text("Process Automatics", size=26, weight=ft.FontWeight.BOLD, color=INK),
                    ],
                    spacing=10,
                ),
                ft.Text(
                    "Ejecuta procesos automaticos y visualiza salida de consola en vivo",
                    size=13,
                    color=SLATE_400,
                ),
                self.toggle_button,
                self.ssh_actions,
                section_title(ft.Icons.TERMINAL, "Proceso"),
                self.log_output,
                section_title(ft.Icons.SUMMARIZE, "Resumen"),
                self.summary,
            ],
            spacing=12,
            expand=True,
        )

    def _toggle_ssh_actions(self, _):
        self.ssh_actions.visible = not self.ssh_actions.visible
        self.update()

    def _append_log(self, text: str):
        if text.startswith("Resumen final"):
            self.summary.visible = True
            self.summary.content.controls[1].value = text
        else:
            self.log_output.value += f"{text}\n"

        self._page.update()

    def _run_process(self, _):
        self.run_button.disabled = True
        self.log_output.value = ""
        self.summary.visible = False
        self.summary.content.controls[1].value = ""
        self._page.update()

        def runner():
            try:
                self.controller.ejecutar(self._append_log)
            finally:
                self.run_button.disabled = False
                self._page.update()

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()