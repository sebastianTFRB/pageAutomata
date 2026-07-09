import flet as ft

from GUI.theme import AMBER_400, DANGER, GREEN_700, INK, NAVY_800, SLATE_400


class StatusUpdateProgressDialog:
    """Overlay reutilizable para mostrar avance de actualizacion de estados."""

    def __init__(self, on_state_change=None):
        self._on_state_change = on_state_change

        self._title = ft.Text("Actualizando estado de switches", size=18, weight=ft.FontWeight.BOLD, color=INK)
        self._subtitle = ft.Text("Preparando proceso...", size=12, color=SLATE_400)
        self._progress = ft.ProgressBar(value=0, color=AMBER_400, bgcolor=ft.Colors.with_opacity(0.18, "#FFFFFF"))
        self._counter = ft.Text("0/0", size=12, color=SLATE_400)
        self._logs = ft.ListView(expand=True, spacing=6, auto_scroll=True)

        self._close_button = ft.TextButton("Cerrar", disabled=True, on_click=self.close)

        self.overlay = ft.Container(
            visible=False,
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.45, "#000000"),
            alignment=ft.Alignment.CENTER,
            content=ft.Container(
                width=720,
                height=480,
                bgcolor=NAVY_800,
                border_radius=12,
                padding=16,
                content=ft.Column(
                    [
                        self._title,
                        self._subtitle,
                        self._progress,
                        self._counter,
                        ft.Divider(height=12, color=ft.Colors.with_opacity(0.08, "#FFFFFF")),
                        self._logs,
                        ft.Row([self._close_button], alignment=ft.MainAxisAlignment.END),
                    ],
                    spacing=10,
                    expand=True,
                ),
            ),
        )

    def _notify_state_change(self):
        if self._on_state_change is not None:
            self._on_state_change()

    def open(self, total: int):
        self._progress.value = 0
        self._counter.value = f"0/{total}"
        self._subtitle.value = "Iniciando actualizacion por ping..."
        self._subtitle.color = SLATE_400
        self._logs.controls = []
        self._logs.controls.append(ft.Text("Iniciando actualizacion...", size=12, color=SLATE_400))
        self._close_button.disabled = True
        self.overlay.visible = True
        self._notify_state_change()

    def log(self, text: str):
        self._logs.controls.append(ft.Text(text, size=12, color=INK, selectable=True))

    def set_progress(self, current: int, total: int):
        if total <= 0:
            self._progress.value = 0
            self._counter.value = "0/0"
            return

        self._progress.value = current / total
        self._counter.value = f"{current}/{total}"

    def finish(self, summary: str, ok: bool = True):
        self._subtitle.value = summary
        self._subtitle.color = GREEN_700 if ok else DANGER
        self._close_button.disabled = False
        self._notify_state_change()

    def close(self, _=None):
        self.overlay.visible = False
        self._notify_state_change()