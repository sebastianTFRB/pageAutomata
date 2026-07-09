import flet as ft

from GUI.theme import AMBER_600, NAVY_700, SLATE_400, card, section_title


class ProcessSSHPanel(ft.Container):
    """Panel visual para ejecutar el proceso de activacion SSH."""

    def __init__(self, on_run):
        super().__init__(
            content=card(
                content=ft.Column(
                    [
                        section_title(ft.Icons.KEY, "Proceso SSH"),
                        ft.Text(
                            "Esta opcion ejecuta la automatizacion actual de activacion SSH.",
                            size=12,
                            color=SLATE_400,
                        ),
                        ft.ElevatedButton(
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
                        ),
                    ],
                    spacing=10,
                ),
                bgcolor=NAVY_700,
            )
        )

    @property
    def run_button(self):
        # card -> Column -> button en indice 2
        return self.content.content.controls[2]
