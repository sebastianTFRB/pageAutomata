import sys
from pathlib import Path

import flet as ft

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from GUI.widget.app_sell import AppShell
from GUI.screens.devices_screen import DevicesScreen
from GUI.screens.login_screen import LoginScreen
from GUI.screens.architecture_screen import ArchitectureScreen
from GUI.screens.process_automatics_screen import ProcessAutomaticsScreen
from GUI.theme import APP_NAME, NAVY_900



def main(page: ft.Page):

    page.title = APP_NAME
    page.window.width = 1100
    page.window.height = 760
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = NAVY_900
    page.padding = 0

    current_user = {"name": ""}

    devices_screen = DevicesScreen(page)

    process_screen = ProcessAutomaticsScreen(page)

    architecture_screen = ArchitectureScreen(
        page,
        on_data_changed=devices_screen.load_switches,
    )

    shell = None

    def show_login():

        page.controls.clear()

        page.add(
            LoginScreen(
                on_login=handle_login,
            )
        )

        page.update()

    def handle_login(user):

        nonlocal shell

        current_user["name"] = user

        shell = AppShell(
            page=page,
            current_user=current_user,
            devices_screen=devices_screen,
            process_screen=process_screen,
            architecture_screen=architecture_screen,
            on_logout=show_login,
        )

        shell.show()

    show_login()


if __name__ == "__main__":
    ft.run(main)