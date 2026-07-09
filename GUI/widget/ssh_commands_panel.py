import flet as ft

from GUI.theme import (
    AMBER_400,
    AMBER_600,
    GREEN_700,
    INK,
    NAVY_700,
    NAVY_800,
    SLATE_400,
    card,
    section_title,
)


class SSHCommandsPanel(ft.Container):
    """Panel visual para libreria y ejecucion de comandos SSH personalizados."""

    def __init__(self, on_add_command, on_reload_library, on_run_commands):
        # Todo se construye como variable local PRIMERO. No se le asigna
        # nada a `self` antes de llamar a super().__init__(): esa fue la
        # causa del panel en blanco en Flet 0.85.3.
        new_command_input = ft.TextField(
            label="Agregar comando a libreria",
            hint_text="Ej: show system-info",
            width=360,
            color=INK,
            bgcolor=NAVY_800,
            border_color=ft.Colors.with_opacity(0.16, "#FFFFFF"),
            focused_border_color=AMBER_600,
            cursor_color=AMBER_600,
            label_style=ft.TextStyle(color=SLATE_400),
            hint_style=ft.TextStyle(color=SLATE_400),
        )

        library_container = ft.Column(
            [],
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
                [
                    ft.Icon(ft.Icons.ADD, size=16, color=AMBER_400),
                    ft.Text("Agregar", color=INK),
                ],
                spacing=8,
                tight=True,
            ),
            on_click=on_add_command,
            style=ft.ButtonStyle(side=ft.BorderSide(1, AMBER_600)),
        )

        reload_button = ft.OutlinedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.REFRESH, size=16, color=AMBER_400),
                    ft.Text("Recargar", color=INK),
                ],
                spacing=8,
                tight=True,
            ),
            on_click=on_reload_library,
            style=ft.ButtonStyle(side=ft.BorderSide(1, AMBER_600)),
        )

        run_button = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.TERMINAL, color="#0B1D33", size=18),
                    ft.Text("Ejecutar SSH Commands", weight=ft.FontWeight.BOLD, color="#0B1D33"),
                ],
                spacing=8,
                tight=True,
            ),
            bgcolor=GREEN_700,
            on_click=on_run_commands,
        )

        # Unica llamada a super().__init__(), igual que en ProcessSSHPanel
        # (que si renderiza bien), con todo el content ya armado.
        super().__init__(
            content=card(
                content=ft.Column(
                    [
                        section_title(ft.Icons.TERMINAL, "SSH Commands"),
                        ft.Text(
                            "Selecciona comandos de libreria y/o agrega comandos libres para ejecutar por SSH en todos los switches de la base de datos.",
                            size=12,
                            color=SLATE_400,
                        ),
                        ft.Row(
                            [
                                new_command_input,
                                add_button,
                                reload_button,
                            ],
                            wrap=True,
                        ),
                        card(
                            content=ft.Column(
                                [
                                    ft.Text("Libreria de comandos", size=12, color=SLATE_400),
                                    library_container,
                                ],
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

        # Recien AHORA, despues de super().__init__(), guardamos las
        # referencias como atributos para que ProcessAutomaticsScreen
        # pueda seguir accediendo via las properties existentes
        # (self.new_command_input, self.library_container, etc.).
        self.new_command_input = new_command_input
        self.library_container = library_container
        self.custom_commands_input = custom_commands_input
        self.add_button = add_button
        self.reload_button = reload_button
        self.run_button = run_button