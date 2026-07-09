import sys
from pathlib import Path

import flet as ft

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from GUI.screens.devices_screen import DevicesScreen
from GUI.screens.login_screen import LoginScreen
from GUI.screens.architecture_screen import ArchitectureScreen
from GUI.screens.process_automatics_screen import ProcessAutomaticsScreen
from GUI.theme import AMBER_400, AMBER_600, APP_NAME, INK, NAVY_700, NAVY_900, SLATE_400


def main(page: ft.Page):
    page.title = APP_NAME
    page.window.width = 1100
    page.window.height = 760
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = NAVY_900
    page.padding = 0

    current_user = {"name": ""}

    devices_screen = DevicesScreen()
    process_screen = ProcessAutomaticsScreen(page)
    architecture_screen = ArchitectureScreen(page, on_data_changed=devices_screen.load_switches)

    content_host = ft.Container(expand=True, padding=24)
    user_badge = ft.Text("", color=SLATE_400, size=13)

    def open_section(index: int):
        if index == 0:
            devices_screen.load_switches()
            content_host.content = devices_screen
        elif index == 1:
            content_host.content = process_screen
        elif index == 2:
            content_host.content = architecture_screen
        else:
            show_login()
            return

        page.update()

    nav = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=120,
        min_extended_width=170,
        group_alignment=-0.9,
        bgcolor=NAVY_700,
        indicator_color=ft.Colors.with_opacity(0.18, AMBER_600),
        leading=ft.Container(
            content=ft.Icon(ft.Icons.ECO, size=28, color="#2FAE4E"),
            padding=ft.Padding.symmetric(vertical=16, horizontal=0),
        ),
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.DEVICES_OUTLINED,
                selected_icon=ft.Icons.DEVICES,
                label="Devices",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS_SUGGEST_OUTLINED,
                selected_icon=ft.Icons.SETTINGS_SUGGEST,
                label="Process Automatics",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.ACCOUNT_TREE_OUTLINED,
                selected_icon=ft.Icons.ACCOUNT_TREE,
                label="Architecture",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.LOGOUT,
                label="Salir",
            ),
        ],
        on_change=lambda e: open_section(e.control.selected_index),
    )

    header = ft.Container(
        padding=ft.Padding.symmetric(horizontal=24, vertical=16),
        bgcolor=NAVY_700,
        content=ft.Row(
            [
                ft.Icon(ft.Icons.ECO, color="#2FAE4E", size=22),
                ft.Text(f"{APP_NAME} Tool", size=22, weight=ft.FontWeight.BOLD, color=INK),
                ft.Container(expand=True),
                ft.Icon(ft.Icons.PERSON, color=SLATE_400, size=16),
                user_badge,
            ],
            spacing=10,
        ),
    )

    shell = ft.Column(
        [
            header,
            ft.Row(
                [
                    nav,
                    ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, "#FFFFFF")),
                    ft.Container(content=content_host, expand=True),
                ],
                expand=True,
                spacing=0,
            ),
        ],
        expand=True,
        spacing=0,
    )

    def show_shell():
        nav.selected_index = 0
        user_badge.value = f"Sesion: {current_user['name']}"
        page.controls.clear()
        page.add(shell)
        open_section(0)

    def handle_login(user: str):
        current_user["name"] = user
        show_shell()

    def show_login():
        page.controls.clear()
        page.add(LoginScreen(on_login=handle_login))
        page.update()

    show_login()


if __name__ == "__main__":
    ft.run(main)