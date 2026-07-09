import threading

import flet as ft

from modules.excel import ExcelManager
from modules.ping import ping
from GUI.widget.status_update_progress_dialog import StatusUpdateProgressDialog
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
    def __init__(self, page: ft.Page | None = None):
        super().__init__(expand=True)

        self._page = page
        self._switches = []
        self._status_update_running = False
        self.status_progress_dialog = StatusUpdateProgressDialog(on_state_change=self._refresh_ui)

        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre", color=SLATE_400, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("IP", color=SLATE_400, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estado", color=SLATE_400, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("SSH", color=SLATE_400, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Spanning-Tree", color=SLATE_400, weight=ft.FontWeight.BOLD)),
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
                ft.DropdownOption(key="funcionando"),
                ft.DropdownOption(key="inactivo"),
            ],
            value="funcionando",
            color=INK,
            border_color=ft.Colors.with_opacity(0.16, "#FFFFFF"),
            focused_border_color=AMBER_600,
            label_style=ft.TextStyle(color=SLATE_400),
        )
        self.input_ssh = ft.Dropdown(
            label="SSH",
            width=140,
            options=[
                ft.DropdownOption(key="true"),
                ft.DropdownOption(key="false"),
            ],
            value="false",
            color=INK,
            border_color=ft.Colors.with_opacity(0.16, "#FFFFFF"),
            focused_border_color=AMBER_600,
            label_style=ft.TextStyle(color=SLATE_400),
        )
        self.input_spanning_tree = ft.Dropdown(
            label="Spanning-Tree",
            width=160,
            options=[
                ft.DropdownOption(key="true"),
                ft.DropdownOption(key="false"),
            ],
            value="false",
            color=INK,
            border_color=ft.Colors.with_opacity(0.16, "#FFFFFF"),
            focused_border_color=AMBER_600,
            label_style=ft.TextStyle(color=SLATE_400),
        )

        self.form_container = card(
            content=ft.Column(
                [
                    section_title(ft.Icons.ADD_CIRCLE_OUTLINE, "Agregar switch"),
                    ft.Row([self.input_nombre, self.input_ip], wrap=True),
                    ft.Row([self.input_usuario, self.input_password], wrap=True),
                    ft.Row([self.input_zona, self.input_estado, self.input_ssh, self.input_spanning_tree], wrap=True),
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

        main_content = ft.Column(
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
                            on_click=self._auto_update_status,
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
            scroll=ft.ScrollMode.AUTO,
        )

        self.content = ft.Stack(
            [
                main_content,
                self.status_progress_dialog.overlay,
            ],
            expand=True,
        )

        self.load_switches()

    def _refresh_ui(self):
        page = self._page or self.page
        if page is not None:
            page.update()
        else:
            self.update()

    def _format_bool_state(self, value):
        return "Activo" if str(value).strip().lower() == "true" else "Inactivo"

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
                        ft.DataCell(ft.Text(self._format_bool_state(sw.get("ssh", "false")), color="#F5F7FA")),
                        ft.DataCell(ft.Text(self._format_bool_state(sw.get("spanning_tree", "false")), color="#F5F7FA")),
                    ]
                )
            )

        self.table.rows = rows
        self.feedback.value = f"Switches cargados: {len(self._switches)}"

    def _reload(self, _):
        self.load_switches()
        self.update()

    def _auto_update_status(self, _):
        if self._status_update_running:
            self.feedback.value = "La actualizacion de estado ya esta en proceso"
            self.feedback.color = SLATE_400
            self.update()
            return

        switches = ExcelManager("switches.db").obtener_switches()
        switches_validos = [sw for sw in switches if (sw.get("ip") or "").strip()]

        if not switches_validos:
            self.feedback.value = "No hay switches registrados para actualizar"
            self.feedback.color = SLATE_400
            self.update()
            return

        dialog = self.status_progress_dialog

        self._status_update_running = True
        self.feedback.value = "Actualizando estatus..."
        self.feedback.color = SLATE_400
        dialog.open(total=len(switches_validos))
        self._refresh_ui()

        def runner():
            ok = 0
            fail = 0
            db_manager = ExcelManager("switches.db")

            try:
                for idx, sw in enumerate(switches_validos, start=1):
                    ip = (sw.get("ip") or "").strip()
                    nombre = (sw.get("nombre") or "SW").strip()

                    estado = "funcionando" if ping(ip) else "inactivo"
                    if estado == "funcionando":
                        ok += 1
                    else:
                        fail += 1

                    db_manager.actualizar_resultado(sw.get("id"), estado)

                    dialog.log(f"[{idx}/{len(switches_validos)}] {nombre} ({ip}) -> {estado}")
                    dialog.set_progress(idx, len(switches_validos))
                    self._refresh_ui()

                self.load_switches()
                self.feedback.value = f"Estatus actualizado por ping. Funcionando: {ok} | Inactivos: {fail}"
                self.feedback.color = GREEN_700

                dialog.finish(
                    summary=f"Proceso finalizado. Funcionando: {ok} | Inactivos: {fail}",
                    ok=True,
                )

            except Exception as ex:
                self.feedback.value = f"Error actualizando estatus: {ex}"
                self.feedback.color = DANGER

                dialog.log(f"ERROR: {ex}")
                dialog.finish("Proceso finalizado con errores", ok=False)

            finally:
                db_manager.cerrar()
                self._status_update_running = False
                self._refresh_ui()

        threading.Thread(target=runner, daemon=True).start()

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
                estado=self.input_estado.value or "funcionando",
                ssh=self.input_ssh.value or "false",
                spanning_tree=self.input_spanning_tree.value or "false",
            )
            self.feedback.value = f"Switch agregado: {nombre} ({ip})"
            self.feedback.color = GREEN_700

            self.input_nombre.value = ""
            self.input_ip.value = ""
            self.input_usuario.value = ""
            self.input_password.value = ""
            self.input_zona.value = ""
            self.input_estado.value = "funcionando"
            self.input_ssh.value = "false"
            self.input_spanning_tree.value = "false"

            self.load_switches()
            self.update()
        except Exception as ex:
            self.feedback.value = f"Error al agregar switch: {ex}"
            self.feedback.color = DANGER
            self.update()