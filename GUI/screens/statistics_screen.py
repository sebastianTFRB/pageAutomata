import flet as ft

from modules.excel import ExcelManager
from GUI.theme import (
    AMBER_400,
    AMBER_600,
    DANGER,
    GREEN_700,
    INK,
    NAVY_700,
    NAVY_800,
    SLATE_400,
    card,
    section_title,
)


class StatisticsScreen(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True)

        self._page = page
        self._devices = []
        self._max_chart_width = 360

        self.feedback = ft.Text("", size=12, color=SLATE_400)

        self.summary_widget = card(content=ft.Column([], spacing=10), bgcolor=NAVY_700)
        self.chart_widget = card(content=ft.Column([], spacing=10), bgcolor=NAVY_700)

        self.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.QUERY_STATS, color=AMBER_400, size=26),
                        ft.Text("Estadisticas", size=26, weight=ft.FontWeight.BOLD, color=INK),
                    ],
                    spacing=10,
                ),
                ft.Text(
                    "Resumen operativo de dispositivos por tipo y estado",
                    size=13,
                    color=SLATE_400,
                ),
                ft.Row(
                    [
                        ft.OutlinedButton(
                            content=ft.Row(
                                [ft.Icon(ft.Icons.REFRESH, size=16, color=AMBER_400), ft.Text("Recargar estadisticas", color=INK)],
                                spacing=8,
                                tight=True,
                            ),
                            style=ft.ButtonStyle(side=ft.BorderSide(1, AMBER_600)),
                            on_click=self._reload,
                        ),
                    ]
                ),
                self.feedback,
                self.summary_widget,
                self.chart_widget,
            ],
            spacing=12,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        self.load_statistics()

    def _refresh_ui(self):
        if self._page is not None:
            self._page.update()

    def _estado_funcionando(self, estado):
        valor = (estado or "").strip().lower()
        return valor in ("funcionando", "en funcionamiento")

    def _tipo_label(self, value):
        labels = {
            "switch": "Switch",
            "camara": "Camara",
            "workstation": "Workstation",
            "videowall": "Videowall",
            "rack": "Rack",
        }
        return labels.get((value or "").strip().lower(), "Desconocido")

    def _build_metric(self, title, value, color=INK):
        return ft.Container(
            width=180,
            padding=12,
            border_radius=10,
            bgcolor=NAVY_800,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.08, "#FFFFFF")),
            content=ft.Column(
                [
                    ft.Text(title, size=11, color=SLATE_400),
                    ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD, color=color),
                ],
                spacing=4,
                tight=True,
            ),
        )

    def _build_chart_row(self, tipo, funcionando, total, max_total):
        porcentaje = 0 if total == 0 else int((funcionando / total) * 100)

        if max_total <= 0:
            barra_total = 0
            barra_ok = 0
        else:
            barra_total = int((total / max_total) * self._max_chart_width)
            barra_ok = int((funcionando / max_total) * self._max_chart_width)

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(self._tipo_label(tipo), color=INK, size=13, width=120),
                        ft.Text(f"{funcionando}/{total} ({porcentaje}%)", color=SLATE_400, size=12),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Stack(
                    [
                        ft.Container(height=14, width=max(1, barra_total), bgcolor=ft.Colors.with_opacity(0.20, "#FFFFFF"), border_radius=6),
                        ft.Container(height=14, width=max(1, barra_ok), bgcolor=GREEN_700, border_radius=6),
                    ],
                    width=self._max_chart_width,
                    height=14,
                ),
            ],
            spacing=6,
        )

    def load_statistics(self):
        tipos = ["switch", "camara", "workstation", "videowall", "rack"]

        try:
            db = ExcelManager("switches.db")
            db.abrir()
            self._devices = db.obtener_dispositivos("todos")

            total_dispositivos = len(self._devices)
            total_funcionando = 0
            total_sin_funcionar = 0

            conteo_tipo = {tipo: 0 for tipo in tipos}
            estado_tipo = {tipo: {"funcionando": 0, "sin_funcionar": 0} for tipo in tipos}

            for device in self._devices:
                tipo = (device.get("tipo") or "switch").strip().lower()
                if tipo not in conteo_tipo:
                    continue

                conteo_tipo[tipo] += 1

                if self._estado_funcionando(device.get("estado")):
                    total_funcionando += 1
                    estado_tipo[tipo]["funcionando"] += 1
                else:
                    total_sin_funcionar += 1
                    estado_tipo[tipo]["sin_funcionar"] += 1

            self.summary_widget.content = ft.Column(
                [
                    section_title(ft.Icons.DASHBOARD, "Widget 1: Totales y estado por tipo"),
                    ft.Row(
                        [
                            self._build_metric("Dispositivos dados de alta", total_dispositivos, AMBER_400),
                            self._build_metric("Funcionando", total_funcionando, GREEN_700),
                            self._build_metric("Sin funcionar", total_sin_funcionar, DANGER),
                        ],
                        wrap=True,
                        spacing=10,
                    ),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Tipo", color=SLATE_400, weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Total", color=SLATE_400, weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Funcionando", color=SLATE_400, weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Sin funcionar", color=SLATE_400, weight=ft.FontWeight.BOLD)),
                        ],
                        rows=[
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text(self._tipo_label(tipo), color=INK)),
                                    ft.DataCell(ft.Text(str(conteo_tipo[tipo]), color=INK)),
                                    ft.DataCell(ft.Text(str(estado_tipo[tipo]["funcionando"]), color=GREEN_700)),
                                    ft.DataCell(ft.Text(str(estado_tipo[tipo]["sin_funcionar"]), color=DANGER)),
                                ]
                            )
                            for tipo in tipos
                        ],
                        heading_row_color=NAVY_800,
                        border=ft.Border.all(1, ft.Colors.with_opacity(0.08, "#FFFFFF")),
                        border_radius=10,
                        divider_thickness=0.4,
                        column_spacing=22,
                    ),
                ],
                spacing=10,
            )

            max_total = max(conteo_tipo.values()) if conteo_tipo else 0

            self.chart_widget.content = ft.Column(
                [
                    section_title(ft.Icons.BAR_CHART, "Widget 2: Grafica de operatividad por tipo"),
                    ft.Text(
                        "Cada barra muestra el total registrado y su tramo en verde indica los equipos funcionando.",
                        size=12,
                        color=SLATE_400,
                    ),
                    ft.Column(
                        [
                            self._build_chart_row(
                                tipo=tipo,
                                funcionando=estado_tipo[tipo]["funcionando"],
                                total=conteo_tipo[tipo],
                                max_total=max_total,
                            )
                            for tipo in tipos
                        ],
                        spacing=12,
                    ),
                ],
                spacing=10,
            )

            self.feedback.value = f"Estadisticas actualizadas. Total de dispositivos: {total_dispositivos}"
            self.feedback.color = SLATE_400

        except Exception as ex:
            self.feedback.value = f"Error cargando estadisticas: {ex}"
            self.feedback.color = DANGER

        self._refresh_ui()

    def _reload(self, _):
        self.load_statistics()
