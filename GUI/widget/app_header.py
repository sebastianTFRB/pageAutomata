import asyncio
import random  # Para simular la variación de velocidad de una terminal real
import flet as ft

from GUI.theme import (
    NAVY_700,
    SLATE_400,
    INK,
)

# Naranja fósforo de consola clásico (Amber Terminal)
CONSOLE_ORANGE = "#FF9100"


class AppHeader(ft.Container):
    """Header con logo animado estilo consola interactiva retro."""

    def __init__(self):
        self.user_badge = ft.Text(
            "",
            color=SLATE_400,
            size=13,
        )

        self.full_text = "> MaintoLabSL ECHOSECURE"

        self.brand_text = ft.Text(
            "",
            size=20,
            weight=ft.FontWeight.W_600,
            color=CONSOLE_ORANGE,  # Aplicamos el naranja de consola
            font_family="monospace",  # Fuente limpia de terminal
            style=ft.TextStyle(letter_spacing=1.5),  # Espaciado premium
            selectable=False,
        )

        # El bloque cursor clásico de terminal
        # Cursor en bloque con ancho ajustable
        self.cursor = ft.Container(
            width=10,  # <-- ¡Baja este número (ej: 6 u 8) si lo quieres aún más delgado!
            height=22,
            bgcolor=CONSOLE_ORANGE,
        )

        self.brand = ft.Row(
            [
                self.brand_text,
                self.cursor,
            ],
            spacing=2,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self._started = False

        super().__init__(
            # Flet 1.0 padding simplificado
            # ✔️ Opción 1: Usar el helper simétrico (La más recomendada y limpia)
            #padding=ft.padding.symmetric(horizontal=24, vertical=16),

            # ✔️ Opción 2: Usar la clase base pura (Llamando cada lado)
            padding=ft.Padding(left=24, right=24, top=16, bottom=16),
            bgcolor=NAVY_700,
            content=ft.Row(
                [
                    self.brand,
                    ft.Container(expand=True),
                    # ✔️ Ícono clásico, minimalista y seguro
                    ft.Icon(
                        ft.Icons.PERSON_OUTLINE, # También puedes usar simplemente ft.Icons.PERSON
                        color=SLATE_400,
                        size=16,
                    ),
                    self.user_badge,
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        )

    def did_mount(self):
        if not self._started:
            self._started = True
            self.page.run_task(self._animate)

    async def _animate(self):
        while True:
            # 1. FASE DE ESCRITURA (Con ligera variación de milisegundos para realismo)
            self.cursor.visible = True
            for i in range(len(self.full_text) + 1):
                self.brand_text.value = self.full_text[:i]
                if not self._safe_update():
                    return
                # Simula pequeños saltos de lag de una terminal real
                await asyncio.sleep(random.uniform(0.04, 0.08))

            # 2. FASE DE ESPERA / PARPADEO (El cursor parpadea al final de la línea)
            for _ in range(6):
                self.cursor.visible = not self.cursor.visible
                if not self._safe_update():
                    return
                await asyncio.sleep(0.4)

            # 3. FASE DE BORRADO (Efecto Backspace interactivo y veloz)
            self.cursor.visible = True
            for i in range(len(self.full_text), -1, -1):
                self.brand_text.value = self.full_text[:i]
                if not self._safe_update():
                    return
                await asyncio.sleep(0.02)  # El borrado es más rápido que la escritura

            # Pausa dramática antes de reiniciar el ciclo
            await asyncio.sleep(0.6)

    def set_user(self, username: str):
        self.user_badge.value = f"Sesión: {username}"
        self._safe_update()

    def _safe_update(self) -> bool:
        try:
            self.update()
            return True
        except RuntimeError:
            return False