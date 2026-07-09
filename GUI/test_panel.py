import sys
from pathlib import Path

import flet as ft

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import flet as ft
from GUI.theme import card, section_title, NAVY_700, NAVY_800, SLATE_400, INK


import flet as ft
from GUI.theme import (
    AMBER_400, AMBER_600, GREEN_700, INK, NAVY_700, NAVY_800, SLATE_400,
    card, section_title,
)


def main(page: ft.Page):
    new_command_input = ft.TextField(
        label="Agregar comando a libreria",
        hint_text="Ej: show system-info",
        color=INK,
        bgcolor=NAVY_800,
        border_color=ft.Colors.with_opacity(0.16, "#FFFFFF"),
        focused_border_color=AMBER_600,
        cursor_color=AMBER_600,
        label_style=ft.TextStyle(color=SLATE_400),
        hint_style=ft.TextStyle(color=SLATE_400),
    )

    library_container = ft.Column(
        [ft.Checkbox(label="show version"), ft.Checkbox(label="show interface")],
        spacing=6,
        scroll=ft.ScrollMode.AUTO,
        height=150,
    )

    custom_commands_input = ft.TextField(
        label="Comandos libres (uno por linea)",
        multiline=True,
        min_lines=3,
        max_lines=6,
        color=INK,
        bgcolor=NAVY_800,
        border_color=ft.Colors.with_opacity(0.16, "#FFFFFF"),
        focused_border_color=AMBER_600,
        cursor_color=AMBER_600,
        label_style=ft.TextStyle(color=SLATE_400),
        hint_style=ft.TextStyle(color=SLATE_400),
        hint_text="show logging\nshow lldp neighbors",
    )

    add_button = ft.OutlinedButton(
        content=ft.Row(
            [ft.Icon(ft.Icons.ADD, size=16, color=AMBER_400), ft.Text("Agregar", color=INK)],
            spacing=8, tight=True,
        ),
        on_click=lambda e: None,
        style=ft.ButtonStyle(side=ft.BorderSide(1, AMBER_600)),
    )

    reload_button = ft.OutlinedButton(
        content=ft.Row(
            [ft.Icon(ft.Icons.REFRESH, size=16, color=AMBER_400), ft.Text("Recargar", color=INK)],
            spacing=8, tight=True,
        ),
        on_click=lambda e: None,
        style=ft.ButtonStyle(side=ft.BorderSide(1, AMBER_600)),
    )

    run_button = ft.ElevatedButton(
        content=ft.Row(
            [ft.Icon(ft.Icons.TERMINAL, color="#0B1D33", size=18),
             ft.Text("Ejecutar SSH Commands", weight=ft.FontWeight.BOLD, color="#0B1D33")],
            spacing=8, tight=True,
        ),
        bgcolor=GREEN_700,
        on_click=lambda e: None,
    )

    page.add(
        card(
            content=ft.Column(
                [
                    section_title(ft.Icons.TERMINAL, "SSH Commands"),
                    ft.Text("Selecciona comandos...", size=12, color=SLATE_400),
                    ##ft.Row(
                     #   [ft.Container(content=new_command_input, expand=True), add_button, reload_button],
                        #wrap=True,
                    #),
                    card(
                        content=ft.Column(
                            [ft.Text("Libreria de comandos", size=12, color=SLATE_400), library_container],
                            spacing=8,
                        ),
                        padding=12,
                        bgcolor=NAVY_800,
                    ),
                    custom_commands_input,
                    run_button,
                ],
                spacing=10,
            ),
            bgcolor=NAVY_700,
        )
    )


ft.run(main)