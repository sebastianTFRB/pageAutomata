import csv
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook

from modules.logger import log


class ExcelManager:

    def __init__(self, archivo):

        self.archivo = str(archivo)
        self.wb = None
        self.ws = None
        self.conn = None
        self.cursor = None
        self.is_sqlite = self.archivo.lower().endswith((".db", ".sqlite", ".sqlite3"))

    def __del__(self):

        self.cerrar()

    def _crear_directorio(self):

        directorio = os.path.dirname(self.archivo)

        if directorio:
            os.makedirs(directorio, exist_ok=True)

    def _crear_tabla(self):

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS switches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                ip TEXT,
                usuario TEXT,
                password TEXT,
                zona TEXT,
                estado TEXT,
                ssh TEXT,
                spanning_tree TEXT,
                fecha TEXT,
                falla TEXT,
                observacion TEXT
            )
            """
        )

        # Migra columnas faltantes en bases antiguas.
        self._asegurar_columna("switches", "spanning_tree", "TEXT")

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ssh_command_library (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comando TEXT NOT NULL UNIQUE,
                descripcion TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

        self.conn.commit()

    def _asegurar_columna(self, tabla, columna, tipo_sql):

        self.cursor.execute(f"PRAGMA table_info({tabla})")
        columnas = [fila[1] for fila in self.cursor.fetchall()]

        if columna in columnas:
            return

        self.cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {tipo_sql}")

    def abrir(self):

        self._crear_directorio()

        if self.is_sqlite:

            log.info(f"Abriendo SQLite: {self.archivo}")

            self.conn = sqlite3.connect(self.archivo)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            self._crear_tabla()

            return

        log.info(f"Abriendo Excel: {self.archivo}")

        if os.path.exists(self.archivo):
            self.wb = load_workbook(self.archivo)
        else:
            self.wb = Workbook()
            self.ws = self.wb.active
            self.ws.title = "Switches"
            self.ws.append([
                "id",
                "nombre",
                "ip",
                "usuario",
                "password",
                "zona",
                "estado",
                "ssh",
                "spanning_tree",
                "fecha",
                "falla",
                "observacion"
            ])
            self.wb.save(self.archivo)

        self.ws = self.wb.active

    def _normalizar(self, valor):

        if valor is None:
            return ""

        return str(valor).strip()

    def _insertar_switch(self, datos):

        self.cursor.execute(
            """
            INSERT INTO switches (
                nombre,
                ip,
                usuario,
                password,
                zona,
                estado,
                ssh,
                spanning_tree,
                fecha,
                falla,
                observacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self._normalizar(datos.get("nombre")),
                self._normalizar(datos.get("ip")),
                self._normalizar(datos.get("usuario")),
                self._normalizar(datos.get("password")),
                self._normalizar(datos.get("zona")),
                self._normalizar(datos.get("estado") or "en funcionamiento"),
                self._normalizar(datos.get("ssh")),
                self._normalizar(datos.get("spanning_tree")),
                self._normalizar(datos.get("fecha") or datetime.now().date().isoformat()),
                self._normalizar(datos.get("falla")),
                self._normalizar(datos.get("observacion"))
            )
        )

    def importar_desde_csv(self, ruta_csv):

        if self.conn is None:
            self.abrir()

        with open(ruta_csv, newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)

            for row in reader:
                self._insertar_switch(row)

        self.conn.commit()
        self.cerrar()

        log.info(f"CSV importado desde {ruta_csv}")

    def importar_desde_excel(self, ruta_excel):

        if self.conn is None:
            self.abrir()

        workbook = load_workbook(ruta_excel)
        sheet = workbook.active

        headers = {}
        for col_idx, cell in enumerate(sheet[1], 1):
            if cell.value:
                headers[str(cell.value).lower().strip()] = col_idx

        log.info(f"Headers detectados: {headers}")
        log.info(f"Filas totales en Excel: {sheet.max_row}")

        contador = 0
        for fila in range(2, sheet.max_row + 1):
            datos = {}

            for campo in ["nombre", "ip", "usuario", "password", "zona", "estado", "ssh", "spanning_tree", "fecha"]:
                col_idx = headers.get(campo)
                if col_idx is None:
                    for key in headers:
                        if campo in key.lower():
                            col_idx = headers[key]
                            break
                
                if col_idx:
                    valor = sheet.cell(row=fila, column=col_idx).value
                    datos[campo] = valor if valor else ""
                else:
                    datos[campo] = ""

            ip_valor = datos.get("ip")
            log.info(f"Fila {fila}: IP={ip_valor}, Nombre={datos.get('nombre')}")

            if not ip_valor:
                continue

            self._insertar_switch(datos)
            contador += 1

        self.conn.commit()
        self.cerrar()

        log.info(f"Excel importado desde {ruta_excel} - {contador} registros insertados")

    def obtener_switches(self):

        if self.is_sqlite:
            if self.conn is None:
                self.abrir()

            self.cursor.execute(
                """
                SELECT id, nombre, ip, usuario, password, zona, estado, ssh, spanning_tree, fecha, falla, observacion
                FROM switches
                ORDER BY id
                """
            )

            filas = self.cursor.fetchall()

            switches = []

            for fila in filas:
                switches.append({
                    "id": fila[0],
                    "nombre": self._normalizar(fila[1]),
                    "ip": self._normalizar(fila[2]),
                    "usuario": self._normalizar(fila[3]),
                    "password": self._normalizar(fila[4]),
                    "zona": self._normalizar(fila[5]),
                    "estado": self._normalizar(fila[6]),
                    "ssh": self._normalizar(fila[7]),
                    "spanning_tree": self._normalizar(fila[8]),
                    "fecha": self._normalizar(fila[9]),
                    "falla": self._normalizar(fila[10]),
                    "observacion": self._normalizar(fila[11])
                })

            log.info(f"Se encontraron {len(switches)} switches")

            self.cerrar()

            return switches

        if self.ws is None:
            self.abrir()

        switches = []

        for fila in range(2, self.ws.max_row + 1):

            ip = self.ws[fila][4].value          # Columna E
            usuario = self.ws[fila][8].value    # Columna I
            password = self.ws[fila][9].value   # Columna J
            nombre = self.ws[fila][12].value    # Columna M

            if not ip:
                continue

            switches.append({

                "fila": fila,

                "nombre": nombre,

                "ip": str(ip).strip(),

                "usuario": str(usuario).strip(),

                "password": str(password).strip(),
                "zona": "",
                "estado": "en funcionamiento",
                "ssh": "",
                "spanning_tree": "",
                "fecha": ""

            })

        log.info(f"Se encontraron {len(switches)} switches")

        return switches

    def actualizar_resultado(

        self,
        fila,
        estado,
        falla="",
        observacion=""
    ):

        if self.is_sqlite:
            if self.conn is None:
                self.abrir()

            self.cursor.execute(
                "UPDATE switches SET estado = ?, falla = ?, observacion = ? WHERE id = ?",
                (estado, falla, observacion, fila)
            )
            self.conn.commit()
            return

        self.ws[fila][13].value = estado        # N
        self.ws[fila][14].value = falla         # O
        self.ws[fila][15].value = observacion   # P

    def exportar_csv(self, ruta_csv):

        if self.conn is None:
            self.abrir()

        switches = self.obtener_switches()

        with open(ruta_csv, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["id", "nombre", "ip", "usuario", "password", "zona", "estado", "ssh", "spanning_tree", "fecha"]
            )
            writer.writeheader()

            for switch in switches:
                writer.writerow({
                    "id": switch.get("id", ""),
                    "nombre": switch.get("nombre", ""),
                    "ip": switch.get("ip", ""),
                    "usuario": switch.get("usuario", ""),
                    "password": switch.get("password", ""),
                    "zona": switch.get("zona", ""),
                    "estado": switch.get("estado", ""),
                    "ssh": switch.get("ssh", ""),
                    "spanning_tree": switch.get("spanning_tree", ""),
                    "fecha": switch.get("fecha", "")
                })

        self.cerrar()

        log.info(f"CSV exportado hacia {ruta_csv}")

    def exportar_excel(self, ruta_excel):

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Switches"
        sheet.append(["id", "nombre", "ip", "usuario", "password", "zona", "estado", "ssh", "spanning_tree", "fecha"])

        for switch in self.obtener_switches():
            sheet.append([
                switch.get("id", ""),
                switch.get("nombre", ""),
                switch.get("ip", ""),
                switch.get("usuario", ""),
                switch.get("password", ""),
                switch.get("zona", ""),
                switch.get("estado", ""),
                switch.get("ssh", ""),
                switch.get("spanning_tree", ""),
                switch.get("fecha", "")
            ])

        workbook.save(ruta_excel)

        self.cerrar()

        log.info(f"Excel exportado hacia {ruta_excel}")

    def cerrar(self):

        if self.conn is not None:
            try:
                self.conn.commit()
            except sqlite3.Error:
                pass

            try:
                self.conn.close()
            except sqlite3.Error:
                pass

            self.conn = None
            self.cursor = None

    def agregar_switch(self, nombre, ip, usuario="", password="", zona="", estado="en funcionamiento", ssh="", spanning_tree="", fecha=""):

        if self.conn is None:
            self.abrir()

        datos = {
            "nombre": nombre,
            "ip": ip,
            "usuario": usuario,
            "password": password,
            "zona": zona,
            "estado": estado,
            "ssh": ssh,
            "spanning_tree": spanning_tree,
            "fecha": fecha or datetime.now().date().isoformat()
        }

        self._insertar_switch(datos)
        self.conn.commit()

        log.info(f"Switch agregado: {nombre} ({ip})")

    def obtener_comandos_ssh(self):

        if not self.is_sqlite:
            return []

        if self.conn is None:
            self.abrir()

        self.cursor.execute(
            """
            SELECT id, comando, descripcion, created_at
            FROM ssh_command_library
            ORDER BY comando COLLATE NOCASE
            """
        )

        filas = self.cursor.fetchall()

        comandos = []
        for fila in filas:
            comandos.append(
                {
                    "id": fila[0],
                    "comando": self._normalizar(fila[1]),
                    "descripcion": self._normalizar(fila[2]),
                    "created_at": self._normalizar(fila[3]),
                }
            )

        return comandos

    def agregar_comando_ssh(self, comando, descripcion=""):

        if not self.is_sqlite:
            return

        comando_limpio = self._normalizar(comando)
        descripcion_limpia = self._normalizar(descripcion)

        if not comando_limpio:
            raise ValueError("El comando no puede estar vacio")

        if self.conn is None:
            self.abrir()

        self.cursor.execute(
            """
            INSERT OR IGNORE INTO ssh_command_library (comando, descripcion, created_at)
            VALUES (?, ?, ?)
            """,
            (
                comando_limpio,
                descripcion_limpia,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        self.conn.commit()

        if self.cursor.rowcount == 0:
            raise ValueError("Ese comando ya existe en la libreria")

        log.info(f"Comando agregado a libreria SSH: {comando_limpio}")

    def guardar(self):

        if self.is_sqlite:
            if self.conn is not None:
                self.conn.commit()

            log.info("SQLite guardado")
            return

        self.wb.save(self.archivo)

        log.info("Excel guardado")