import math
import flet as ft

# Asumiendo que mantienes estas constantes en tu archivo de tema
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
    FIXED_USER = "SebastianAdmin"
    FIXED_PASSWORD = "315680"

    def __init__(self, on_login):
        super().__init__(expand=True)
        self.on_login = on_login

        # ---- Inputs con estilo más "Sharp" y tecnológico ----
        self.user_input = ft.TextField(
            label="Usuario de Red",
            width=320,
            autofocus=True,
            color=ft.Colors.WHITE,
            border_color=NAVY_700,
            focused_border_color=GREEN_500,
            cursor_color=GREEN_500,
            prefix_icon=ft.Icons.PERSON_OUTLINED,
            label_style=ft.TextStyle(color=SLATE_400),
            text_size=14,
            height=60,
        )
        self.password_input = ft.TextField(
            label="Clave de Acceso",
            width=320,
            password=True,
            can_reveal_password=True,
            color=ft.Colors.WHITE,
            border_color=NAVY_700,
            focused_border_color=AMBER_600,
            cursor_color=AMBER_600,
            prefix_icon=ft.Icons.LOCK_OUTLINED,
            label_style=ft.TextStyle(color=SLATE_400),
            text_size=14,
            height=60,
        )
        self.error_text = ft.Text("", color=DANGER, size=12, weight=ft.FontWeight.W_500)

        # ---- Nuevo Logo: Escudo Digital + Ondas (EchoSecure) ----
        logo_icon = ft.Stack(
            [
                # Círculos de "Echo" (Ondas)
                ft.Container(
                    width=60, height=60,
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.2, GREEN_500)),
                    border_radius=30,
                    animate_scale=ft.Animation(1000, ft.AnimationCurve.EASE_OUT),
                ),
                ft.Container(
                    width=44, height=44,
                    bgcolor=ft.Colors.with_opacity(0.1, GREEN_500),
                    border=ft.Border.all(2, GREEN_500),
                    border_radius=12,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Icon(ft.Icons.SECURITY, color=AMBER_400, size=24),
                ),
            ],
            alignment=ft.Alignment.CENTER,
        )

        logo_text = ft.Row(
            [
                ft.Text("ECHO", size=32, weight=ft.FontWeight.W_900, color=GREEN_500, style=ft.TextStyle(letter_spacing=2)),
                ft.Text("SECURE", size=32, weight=ft.FontWeight.W_300, color=AMBER_400, style=ft.TextStyle(letter_spacing=2)),
            ],
            spacing=4,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        # ---- NUEVO: Formas geométricas de fondo ----
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
                shape(420, BLUE_500, 0.25, top=-140, left=-120),
                shape(300, AMBER_600, 0.12, bottom=-100, right=-80),
                shape(220, BLUE_300, 0.08, top=70, right=-60, radius=40, rot=math.pi / 4),
                shape(140, GREEN_500, 0.06, bottom=50, left=70, radius=28, rot=math.pi / 6),
            ],
            expand=True,
        )

        # ---- Tarjeta de Login (Cyber-Panel) ----
        card = ft.Container(
            width=400,
            padding=ft.Padding.symmetric(horizontal=40, vertical=50),
            border_radius=24,
            bgcolor=NAVY_900, 
            border=ft.Border.all(1, NAVY_700),
            shadow=ft.BoxShadow(
                blur_radius=50,
                color=ft.Colors.with_opacity(0.5, "#000000"),
                offset=ft.Offset(0, 25),
            ),
            content=ft.Column(
                [
                    logo_icon,
                    ft.Container(height=10),
                    logo_text,
                    ft.Text(
                        "SECURITY PROTOCOL ACTIVE", 
                        size=10, 
                        color=BLUE_300, 
                        weight=ft.FontWeight.BOLD,
                        style=ft.TextStyle(letter_spacing=1.5)
                    ),
                    ft.Container(height=20),
                    self.user_input,
                    self.password_input,
                    self.error_text,
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        content=ft.Row(
                            [
                                ft.Text("ESTABLECER CONEXIÓN", weight=ft.FontWeight.BOLD),
                                ft.Icon(ft.Icons.WIFI_TETHERING, size=18),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        width=320,
                        height=50,
                        bgcolor=GREEN_500,
                        color=NAVY_900,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                        on_click=self._submit,
                    ),
                    ft.TextButton(
                        "¿Olvidó sus credenciales?",
                        style=ft.ButtonStyle(color=SLATE_400),
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
        )

        # ---- NUEVO: Fondo aclarado con el Stack de formas fijado ----
        self.bgcolor = "#1E293B" # Gris azulado intermedio, mucho más claro que el anterior
        self.content = ft.Stack(
            [
                background_shapes, # Capa de esferas y cubos traseros
                ft.Container(
                    content=card, 
                    alignment=ft.Alignment.CENTER,
                ),
                # Decoración de esquina: Versión del software
                ft.Container(
                    content=ft.Text("v2.4.0-STABLE", color=SLATE_400, size=10, weight=ft.FontWeight.BOLD),
                    bottom=20,
                    right=30,
                )
            ],
            expand=True,
        )

    def _submit(self, _):
        user = self.user_input.value.strip()
        password = self.password_input.value.strip()

        if not user or not password:
            self.error_text.value = "ERROR: Credenciales requeridas"
            self.user_input.border_color = DANGER
            self.password_input.border_color = DANGER
            self.update()
            return

        if user != self.FIXED_USER or password != self.FIXED_PASSWORD:
            self.error_text.value = "ERROR: Usuario o contrasena incorrecta"
            self.user_input.border_color = DANGER
            self.password_input.border_color = DANGER
            self.update()
            return

        self.error_text.value = ""
        self.user_input.border_color = NAVY_700
        self.password_input.border_color = NAVY_700
        self.update()
        self.on_login(user)