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


class DevicesScreen(ft.Container):
    def __init__(self):
        super().__init__(expand=True)

        self._switches = []

        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre", color=SLATE_400, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("IP", color=SLATE_400, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estado", color=SLATE_400, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("SSH", color=SLATE_400, weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            column_spacing=18,
            data_row_min_height=36,
            data_row_max_height=48,
            heading_row_color=NAVY_800,
            divider_thickness=0.4,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.08, "#FFFFFF")),
            border_radius=10,
        )

        self.feedback = ft.Text("", size=12, color=SLATE_400)

        self.form_visible = False

        field_style = dict(
            color=INK,
            border_color=ft.Colors.with_opacity(0.16, "#FFFFFF"),
            focused_border_color=AMBER_600,
            cursor_color=AMBER_600,
            label_style=ft.TextStyle(color=SLATE_400),
        )

        self.input_nombre = ft.TextField(label="Nombre *", width=220, **field_style)
        self.input_ip = ft.TextField(label="IP *", width=180, **field_style)
        self.input_usuario = ft.TextField(label="Usuario", width=180, **field_style)
        self.input_password = ft.TextField(
            label="Contrasena", width=180, password=True, can_reveal_password=True, **field_style
        )
        self.input_zona = ft.TextField(label="Zona", width=160, **field_style)
        self.input_estado = ft.Dropdown(
            label="Estado",
            width=200,
            options=[
                ft.DropdownOption(key="en funcionamiento"),
                ft.DropdownOption(key="sin funcionamiento"),
                ft.DropdownOption(key="mantenimiento"),
            ],
            value="en funcionamiento",
            color=INK,
            border_color=ft.Colors.with_opacity(0.16, "#FFFFFF"),
            focused_border_color=AMBER_600,
            label_style=ft.TextStyle(color=SLATE_400),
        )
        self.input_ssh = ft.TextField(label="SSH", width=120, **field_style)

        self.form_container = card(
            content=ft.Column(
                [
                    section_title(ft.Icons.ADD_CIRCLE_OUTLINE, "Agregar switch"),
                    ft.Row([self.input_nombre, self.input_ip], wrap=True),
                    ft.Row([self.input_usuario, self.input_password], wrap=True),
                    ft.Row([self.input_zona, self.input_estado, self.input_ssh], wrap=True),
                    ft.ElevatedButton(
                        content=ft.Text("Guardar switch", weight=ft.FontWeight.BOLD, color="#0B1D33"),
                        bgcolor=AMBER_600,
                        on_click=self._add_switch,
                    ),
                ],
                spacing=10,
            ),
        )
        self.form_container.visible = False

        self.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.DEVICES, color=AMBER_400, size=26),
                        ft.Text("Devices", size=26, weight=ft.FontWeight.BOLD, color=INK),
                    ],
                    spacing=10,
                ),
                ft.Text("Listado de switches y estado actual", size=13, color=SLATE_400),
                ft.Row(
                    [
                        ft.OutlinedButton(
                            content=ft.Row(
                                [ft.Icon(ft.Icons.REFRESH, size=16, color=AMBER_400), ft.Text("Recargar lista", color=INK)],
                                spacing=8, tight=True,
                            ),
                            on_click=self._reload,
                            style=ft.ButtonStyle(side=ft.BorderSide(1, AMBER_600)),
                        ),
                        ft.OutlinedButton(
                            content=ft.Row(
                                [ft.Icon(ft.Icons.SYNC, size=16, color=AMBER_400), ft.Text("Actualizar estatus automaticamente", color=INK)],
                                spacing=8, tight=True,
                            ),
                            on_click=self._dummy_auto_status,
                            style=ft.ButtonStyle(side=ft.BorderSide(1, AMBER_600)),
                        ),
                        ft.OutlinedButton(
                            content=ft.Row(
                                [ft.Icon(ft.Icons.ADD, size=16, color=AMBER_400), ft.Text("Mostrar formulario para agregar SW", color=INK)],
                                spacing=8, tight=True,
                            ),
                            on_click=self._toggle_form,
                            style=ft.ButtonStyle(side=ft.BorderSide(1, AMBER_600)),
                        ),
                    ],
                    wrap=True,
                ),
                self.feedback,
                self.form_container,
                card(
                    content=ft.ListView([self.table], expand=True, spacing=0),
                    bgcolor=NAVY_700,
                    padding=8,
                ),
            ],
            spacing=12,
            expand=True,
        )

        self.load_switches()

    def load_switches(self):
        db_manager = ExcelManager("switches.db")
        db_manager.abrir()
        self._switches = db_manager.obtener_switches()

        rows = []
        for sw in self._switches:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(sw.get("nombre", ""), color="#F5F7FA")),
                        ft.DataCell(ft.Text(sw.get("ip", ""), color="#F5F7FA")),
                        ft.DataCell(ft.Text(sw.get("estado", ""), color="#F5F7FA")),
                        ft.DataCell(ft.Text(sw.get("ssh", ""), color="#F5F7FA")),
                    ]
                )
            )

        self.table.rows = rows
        self.feedback.value = f"Switches cargados: {len(self._switches)}"

    def _reload(self, _):
        self.load_switches()
        self.update()

    def _dummy_auto_status(self, _):
        self.feedback.value = "Actualizacion automatica de estatus: pendiente de implementacion"
        self.update()

    def _toggle_form(self, _):
        self.form_visible = not self.form_visible
        self.form_container.visible = self.form_visible
        self.update()

    def _add_switch(self, _):
        nombre = self.input_nombre.value.strip()
        ip = self.input_ip.value.strip()

        if not nombre or not ip:
            self.feedback.value = "Error: Nombre e IP son obligatorios"
            self.feedback.color = DANGER
            self.update()
            return

        try:
            db_manager = ExcelManager("switches.db")
            db_manager.agregar_switch(
                nombre=nombre,
                ip=ip,
                usuario=self.input_usuario.value or "",
                password=self.input_password.value or "",
                zona=self.input_zona.value or "",
                estado=self.input_estado.value or "en funcionamiento",
                ssh=self.input_ssh.value or "",
            )
            self.feedback.value = f"Switch agregado: {nombre} ({ip})"
            self.feedback.color = GREEN_700

            self.input_nombre.value = ""
            self.input_ip.value = ""
            self.input_usuario.value = ""
            self.input_password.value = ""
            self.input_zona.value = ""
            self.input_estado.value = "en funcionamiento"
            self.input_ssh.value = ""

            self.load_switches()
            self.update()
        except Exception as ex:
            self.feedback.value = f"Error al agregar switch: {ex}"
            self.feedback.color = DANGER
            self.update()