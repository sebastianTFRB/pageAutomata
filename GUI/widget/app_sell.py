import flet as ft

from GUI.theme import (
    AMBER_400,
    AMBER_600,
    NAVY_700,
)
from GUI.widget.app_header import AppHeader


class AppShell(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        current_user: dict,
        devices_screen,
        process_screen,
        architecture_screen,
        statistics_screen,
        on_logout,
    ):
        super().__init__(expand=True)

        self.host_page = page
        self.current_user = current_user
        self.on_logout = on_logout

        self.devices_screen = devices_screen
        self.process_screen = process_screen
        self.architecture_screen = architecture_screen
        self.statistics_screen = statistics_screen

        # Transiciones suaves al montar shell y navegación.
        self.animate_opacity = 400
        self.animate_scale = 400

        self.content_host = ft.Container(
            expand=True,
            padding=24,
        )

        self.nav = self._create_nav()
        self.header = AppHeader()

        self.content = ft.Column(
            [
                self.header,
                ft.Row(
                    [
                        self.nav,
                        ft.VerticalDivider(
                            width=1,
                            color=ft.Colors.with_opacity(0.08, "#FFFFFF"),
                        ),
                        ft.Container(
                            content=self.content_host,
                            expand=True,
                        ),
                    ],
                    expand=True,
                    spacing=0,
                ),
            ],
            expand=True,
            spacing=0,
        )

    def _create_nav(self):

        return ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=120,
            min_extended_width=170,
            group_alignment=-0.9,
            bgcolor=NAVY_700,
            indicator_color=ft.Colors.with_opacity(
                0.18,
                AMBER_600,
            ),
            leading=ft.Container(
                content=ft.Icon(
                    ft.Icons.SECURITY,
                    size=28,
                    color=AMBER_400,
                ),
                padding=ft.Padding.symmetric(vertical=16),
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
                    icon=ft.Icons.QUERY_STATS_OUTLINED,
                    selected_icon=ft.Icons.QUERY_STATS,
                    label="Estadisticas",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.LOGOUT,
                    label="Salir",
                ),
            ],
            on_change=self.change_page,
        )

    def change_page(self, e):

        index = e.control.selected_index

        if index == 0:
            self.devices_screen.load_switches()
            self.content_host.content = self.devices_screen

        elif index == 1:
            self.content_host.content = self.process_screen

        elif index == 2:
            self.content_host.content = self.architecture_screen

        elif index == 3:
            self.statistics_screen.load_statistics()
            self.content_host.content = self.statistics_screen

        else:
            self.on_logout()
            return

        self.host_page.update()

    def show(self):

        self.nav.selected_index = 0

        self.host_page.controls.clear()
        self.host_page.add(self)

        self.header.set_user(self.current_user["name"])

        self.devices_screen.load_switches()
        self.content_host.content = self.devices_screen

        self.host_page.update()
