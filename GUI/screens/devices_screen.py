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
        self._devices = []
        self._status_update_running = False
        self.status_progress_dialog = StatusUpdateProgressDialog(on_state_change=self._refresh_ui)

        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Tipo", color=SLATE_400, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Nombre", color=SLATE_400, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("IP", color=SLATE_400, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Usuario", color=SLATE_400, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estado", color=SLATE_400, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("SSH", color=SLATE_400, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Falla", color=SLATE_400, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Observacion", color=SLATE_400, weight=ft.FontWeight.BOLD)),
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

        self.filter_tipo = ft.Dropdown(
            label="Mostrar",
            width=180,
            options=[
                ft.DropdownOption(key="todos"),
                ft.DropdownOption(key="switch"),
                ft.DropdownOption(key="camara"),
                ft.DropdownOption(key="workstation"),
                ft.DropdownOption(key="videowall"),
                ft.DropdownOption(key="rack"),
            ],
            value="todos",
            color=INK,
            border_color=ft.Colors.with_opacity(0.16, "#FFFFFF"),
            focused_border_color=AMBER_600,
            label_style=ft.TextStyle(color=SLATE_400),
            on_select=self._reload,
        )

        self.input_nombre = ft.TextField(label="Nombre *", width=220, **field_style)
        self.input_ip = ft.TextField(label="IP *", width=180, **field_style)
        self.input_usuario = ft.TextField(label="Usuario", width=180, **field_style)
        self.input_password = ft.TextField(
            label="Contrasena", width=180, password=True, can_reveal_password=True, **field_style
        )
        self.input_tipo = ft.Dropdown(
            label="Tipo",
            width=180,
            options=[
                ft.DropdownOption(key="switch"),
                ft.DropdownOption(key="camara"),
                ft.DropdownOption(key="workstation"),
                ft.DropdownOption(key="videowall"),
                ft.DropdownOption(key="rack"),
            ],
            value="switch",
            color=INK,
            border_color=ft.Colors.with_opacity(0.16, "#FFFFFF"),
            focused_border_color=AMBER_600,
            label_style=ft.TextStyle(color=SLATE_400),
        )
        self.form_help = ft.Text(
            "Alta manual de switches, camaras, workstation, videowall o rack.",
            size=12,
            color=SLATE_400,
        )
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

        self.form_container = card(
            content=ft.Column(
                [
                    section_title(ft.Icons.ADD_CIRCLE_OUTLINE, "Agregar dispositivo"),
                    self.form_help,
                    ft.Row([self.input_nombre, self.input_ip], wrap=True),
                    ft.Row([self.input_tipo, self.input_usuario, self.input_password], wrap=True),
                    ft.Row([self.input_estado, self.input_ssh], wrap=True),
                    ft.ElevatedButton(
                        content=ft.Text("Guardar dispositivo manual", weight=ft.FontWeight.BOLD, color="#0B1D33"),
                        bgcolor=AMBER_600,
                        on_click=self._add_device,
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
                ft.Text("Listado de dispositivos y estado actual", size=13, color=SLATE_400),
                ft.Row([
                    self.filter_tipo,
                ]),
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
                                [ft.Icon(ft.Icons.ADD, size=16, color=AMBER_400), ft.Text("Agregar manualmente", color=INK)],
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

    def _tipo_label(self, value):

        tipo = (value or "").strip().lower()

        if tipo in ("", "all", "todos"):
            return "Todos"

        labels = {
            "switch": "Switch",
            "camara": "Camara",
            "workstation": "Workstation",
            "videowall": "Videowall",
            "rack": "Rack",
        }

        return labels.get(tipo, tipo.title())

    def _refresh_ui(self):
        page = self._page or self.page
        if page is not None:
            page.update()
        else:
            self.update()

    def _format_bool_state(self, value):
        return "Activo" if str(value).strip().lower() == "true" else "Inactivo"

    def _estado_color(self, value):
        estado = (value or "").strip().lower()

        if estado == "funcionando":
            return GREEN_700

        if estado == "inactivo":
            return DANGER

        return SLATE_400

    def load_switches(self):
        self.load_devices()

    def load_devices(self):
        tipo_filtro = self.filter_tipo.value or "todos"
        db_manager = ExcelManager("switches.db")
        db_manager.abrir()
        self._devices = db_manager.obtener_dispositivos(tipo_filtro)
        self._switches = self._devices

        rows = []
        for sw in self._devices:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(self._tipo_label(sw.get("tipo", "switch")), color="#F5F7FA")),
                        ft.DataCell(ft.Text(sw.get("nombre", ""), color="#F5F7FA")),
                        ft.DataCell(ft.Text(sw.get("ip", ""), color="#F5F7FA")),
                        ft.DataCell(ft.Text(sw.get("usuario", ""), color="#F5F7FA")),
                        ft.DataCell(ft.Text(sw.get("estado", ""), color=self._estado_color(sw.get("estado", "")))),
                        ft.DataCell(ft.Text(self._format_bool_state(sw.get("ssh", "false")), color="#F5F7FA")),
                        ft.DataCell(ft.Text(sw.get("falla", ""), color="#F5F7FA")),
                        ft.DataCell(ft.Text(sw.get("observacion", ""), color="#F5F7FA")),
                    ]
                )
            )

        self.table.rows = rows
        self.feedback.value = f"Dispositivos cargados: {len(self._devices)}"

    def _reload(self, _):
        self.load_devices()
        self.update()

    def _auto_update_status(self, _):
        if self._status_update_running:
            self.feedback.value = "La actualizacion de estado ya esta en proceso"
            self.feedback.color = SLATE_400
            self.update()
            return

        dispositivos = ExcelManager("switches.db").obtener_dispositivos(self.filter_tipo.value or "todos")
        switches_validos = [sw for sw in dispositivos if (sw.get("ip") or "").strip()]

        if not switches_validos:
            self.feedback.value = "No hay dispositivos registrados para actualizar"
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
                    falla = "" if estado == "funcionando" else "ping"
                    observacion = "" if estado == "funcionando" else "Sin respuesta al ping"

                    if estado == "funcionando":
                        ok += 1
                    else:
                        fail += 1

                    db_manager.actualizar_resultado(sw.get("id"), estado, falla=falla, observacion=observacion)

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

        if self.form_visible:
            tipo_filtro = self.filter_tipo.value or "todos"
            if tipo_filtro in ("switch", "camara", "workstation", "videowall", "rack"):
                self.input_tipo.value = tipo_filtro

        self.update()

    def _reset_manual_form(self, tipo="switch"):
        self.input_nombre.value = ""
        self.input_ip.value = ""
        self.input_tipo.value = tipo
        self.input_usuario.value = ""
        self.input_password.value = ""
        self.input_estado.value = "funcionando"
        self.input_ssh.value = "false"

    def _add_device(self, _):
        nombre = self.input_nombre.value.strip()
        ip = self.input_ip.value.strip()

        if not nombre or not ip:
            self.feedback.value = "Error: Nombre e IP son obligatorios"
            self.feedback.color = DANGER
            self.update()
            return

        try:
            db_manager = ExcelManager("switches.db")
            db_manager.agregar_dispositivo(
                tipo=self.input_tipo.value or "switch",
                nombre=nombre,
                ip=ip,
                usuario=self.input_usuario.value or "",
                password=self.input_password.value or "",
                estado=self.input_estado.value or "funcionando",
                ssh=self.input_ssh.value or "false",
            )
            self.feedback.value = f"Dispositivo agregado: {nombre} ({ip})"
            self.feedback.color = GREEN_700

            tipo_reinicio = self.filter_tipo.value if self.filter_tipo.value in ("switch", "camara", "workstation", "videowall", "rack") else "switch"
            self._reset_manual_form(tipo_reinicio)

            self.load_devices()
            self.update()
        except Exception as ex:
            self.feedback.value = f"Error al agregar dispositivo: {ex}"
            self.feedback.color = DANGER
            self.update()