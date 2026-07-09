import math

import flet as ft

from GUI.theme import (
    AMBER_400,
    AMBER_600,
    BLUE_300,
    BLUE_500,
    DANGER,
    GREEN_500,
    INK,
    NAVY_700,
    NAVY_900,
    SLATE_400,
)


class LoginScreen(ft.Container):
    def __init__(self, on_login):
        super().__init__(expand=True)
        self.on_login = on_login

        self.user_input = ft.TextField(
            label="Usuario",
            width=320,
            autofocus=True,
            color=INK,
            border_color=SLATE_400,
            focused_border_color=AMBER_600,
            cursor_color=AMBER_600,
            label_style=ft.TextStyle(color=SLATE_400),
        )
        self.password_input = ft.TextField(
            label="Contrasena",
            width=320,
            password=True,
            can_reveal_password=True,
            color=INK,
            border_color=SLATE_400,
            focused_border_color=AMBER_600,
            cursor_color=AMBER_600,
            label_style=ft.TextStyle(color=SLATE_400),
        )
        self.error_text = ft.Text("", color=DANGER, size=12)

        # ---- Logo: badge romboidal ambar + "ECO" (verde) / "SOLUT" (ambar) ----
        logo = ft.Row(
            [
                ft.Container(
                    width=44,
                    height=44,
                    border_radius=12,
                    bgcolor=NAVY_700,
                    border=ft.Border.all(2, AMBER_600),
                    alignment=ft.Alignment.CENTER,
                    rotate=math.pi / 4,
                    content=ft.Container(
                        rotate=-math.pi / 4,
                        content=ft.Icon(ft.Icons.ECO, color=GREEN_500, size=22),
                    ),
                ),
                ft.Row(
                    [
                        ft.Text("ECO", size=28, weight=ft.FontWeight.W_800, color=GREEN_500, style=ft.TextStyle(letter_spacing=1)),
                        ft.Text("SOLUT", size=28, weight=ft.FontWeight.W_800, color=AMBER_400, style=ft.TextStyle(letter_spacing=1)),
                    ],
                    spacing=0,
                ),
            ],
            spacing=14,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        # ---- Formas geometricas de fondo ----
        def shape(size, color, opacity, top=None, left=None, right=None, bottom=None, radius=None, rot=None):
            c = ft.Container(
                width=size,
                height=size,
                bgcolor=ft.Colors.with_opacity(opacity, color),
                border_radius=radius if radius is not None else size,
                rotate=rot,
            )
            c.top, c.left, c.right, c.bottom = top, left, right, bottom
            return c

        background_shapes = ft.Stack(
            [
                shape(420, BLUE_500, 0.35, top=-140, left=-120),
                shape(300, AMBER_600, 0.14, bottom=-100, right=-80),
                shape(220, BLUE_300, 0.10, top=70, right=-60, radius=40, rot=math.pi / 4),
                shape(140, GREEN_500, 0.07, bottom=50, left=70, radius=28, rot=math.pi / 6),
            ],
            expand=True,
        )

        # ---- Tarjeta central (vidrio esmerilado) ----
        card = ft.Container(
            width=380,
            padding=ft.Padding.symmetric(horizontal=36, vertical=40),
            border_radius=20,
            bgcolor=ft.Colors.with_opacity(0.06, "#FFFFFF"),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.14, "#FFFFFF")),
            shadow=ft.BoxShadow(
                blur_radius=40,
                color=ft.Colors.with_opacity(0.35, "#000000"),
                offset=ft.Offset(0, 20),
            ),
            content=ft.Column(
                [
                    logo,
                    ft.Container(height=6),
                    ft.Text(
                        "Inicia sesion para continuar",
                        size=13,
                        color=SLATE_400,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=16),
                    self.user_input,
                    self.password_input,
                    self.error_text,
                    ft.Container(height=6),
                    ft.ElevatedButton(
                        content=ft.Text("Entrar", weight=ft.FontWeight.BOLD, color=NAVY_900),
                        width=320,
                        height=46,
                        bgcolor=AMBER_600,
                        on_click=self._submit,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=14,
            ),
        )

        self.bgcolor = NAVY_900
        self.content = ft.Stack(
            [
                background_shapes,
                ft.Container(content=card, alignment=ft.Alignment.CENTER, expand=True),
            ],
            expand=True,
        )

    def _submit(self, _):
        user = self.user_input.value.strip()
        password = self.password_input.value.strip()

        if not user or not password:
            self.error_text.value = "Usuario y contrasena son obligatorios"
            self.update()
            return

        self.error_text.value = ""
        self.update()
        self.on_login(user)