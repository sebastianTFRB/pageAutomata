import flet as ft

from GUI.theme import AMBER_600, NAVY_700, SLATE_400, card, section_title


class ProcessSSHPanel(ft.Container):
    """Panel visual para ejecutar el proceso de activacion SSH."""

    def __init__(self, on_run, on_toggle_switches, on_select_all_switches, on_clear_all_switches):
        self._switches_list = ft.Column(spacing=6)
        self._switches_panel = ft.Container(
            visible=False,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.TextButton("Seleccionar todos", on_click=on_select_all_switches),
                            ft.TextButton("Limpiar seleccion", on_click=on_clear_all_switches),
                        ],
                        spacing=6,
                        wrap=True,
                    ),
                    ft.Container(
                        content=self._switches_list,
                        height=190,
                        border=ft.Border.all(1, ft.Colors.with_opacity(0.10, "#FFFFFF")),
                        border_radius=10,
                        padding=10,
                    ),
                ],
                spacing=6,
            ),
        )

        self._toggle_switches_button = ft.OutlinedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.EXPAND_MORE, size=16, color="#F5F7FA"),
                    ft.Text("Elegir switches (solo funcionando)", color="#F5F7FA"),
                ],
                spacing=8,
                tight=True,
            ),
            on_click=on_toggle_switches,
        )

        self._run_button = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.PLAY_ARROW, color="#0B1D33", size=18),
                    ft.Text(
                        "Iniciar activacion SSH",
                        weight=ft.FontWeight.BOLD,
                        color="#0B1D33",
                    ),
                ],
                spacing=8,
                tight=True,
            ),
            bgcolor=AMBER_600,
            on_click=on_run,
        )

        super().__init__(
            content=card(
                content=ft.Column(
                    [
                        section_title(ft.Icons.KEY, "Proceso SSH"),
                        ft.Text(
                            "Esta opcion ejecuta la automatizacion de activacion SSH sobre switches en estado funcionando.",
                            size=12,
                            color=SLATE_400,
                        ),
                        self._toggle_switches_button,
                        self._switches_panel,
                        self._run_button,
                    ],
                    spacing=10,
                ),
                bgcolor=NAVY_700,
            )
        )

    @property
    def run_button(self):
        return self._run_button

    @property
    def switches_panel(self):
        return self._switches_panel

    @property
    def switches_list(self):
        return self._switches_list

    @property
    def toggle_switches_button(self):
        return self._toggle_switches_button
