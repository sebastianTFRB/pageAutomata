"""
Tokens de marca MaintoLabSL ECHOSECURE.
Un solo lugar para colores, tipografia y helpers visuales
compartidos entre todas las pantallas.
"""

import flet as ft

APP_NAME = "MaintoLabSL ECHOSECURE"

# ---- Paleta ----
NAVY_900 = "#0B1D33"   # fondo principal
NAVY_800 = "#102943"   # fondo de inputs / consola
NAVY_700 = "#14304F"   # tarjetas / paneles
NAVY_600 = "#1B3A5C"   # hover / bordes activos

BLUE_500 = "#2F6FA0"   # acento azul (formas, iconos secundarios)
BLUE_300 = "#5B90B8"

SLATE_400 = "#8B98A5"  # texto secundario
SLATE_500 = "#6B7A8A"  # texto terciario / placeholders

AMBER_600 = "#C97A1B"  # accion primaria
AMBER_400 = "#E0A028"  # acento calido / hover

GREEN_500 = "#2FAE4E"  # exito / marca (logo)
GREEN_700 = "#1F7A38"

INK = "#F5F7FA"        # texto principal sobre fondo oscuro
DANGER = "#E5484D"

CARD_BORDER = ft.Colors.with_opacity(0.08, "#FFFFFF")


def card(content, padding=16, bgcolor=NAVY_700, radius=14, border_color=None):
    """Panel/tarjeta estandar usada en todas las pantallas."""
    return ft.Container(
        content=content,
        padding=padding,
        border_radius=radius,
        bgcolor=bgcolor,
        border=ft.Border.all(1, border_color or CARD_BORDER),
    )


def section_title(icon, text):
    """Encabezado de seccion: icono + texto, mismo lenguaje visual en toda la app."""
    return ft.Row(
        [
            ft.Icon(icon, color=AMBER_400, size=18),
            ft.Text(text, size=16, weight=ft.FontWeight.BOLD, color=INK),
        ],
        spacing=8,
    )


def primary_button(text, on_click, icon=None, width=None):
    return ft.ElevatedButton(
        content=ft.Row(
            [ft.Icon(icon, size=16, color=NAVY_900)] if icon else [] + [ft.Text(text, weight=ft.FontWeight.BOLD, color=NAVY_900)],
            spacing=8,
            tight=True,
        ) if icon else ft.Text(text, weight=ft.FontWeight.BOLD, color=NAVY_900),
        bgcolor=AMBER_600,
        width=width,
        on_click=on_click,
    )


def outlined_button(text, on_click, icon=None, width=None):
    return ft.OutlinedButton(
        content=ft.Row(
            ([ft.Icon(icon, size=16, color=AMBER_400)] if icon else []) + [ft.Text(text, color=INK)],
            spacing=8,
            tight=True,
        ),
        width=width,
        on_click=on_click,
        style=ft.ButtonStyle(side=ft.BorderSide(1, AMBER_600)),
    )