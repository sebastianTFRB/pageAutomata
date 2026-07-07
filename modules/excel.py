from openpyxl import load_workbook
from modules.logger import log


class ExcelManager:

    def __init__(self, archivo):

        self.archivo = archivo
        self.wb = None
        self.ws = None

    def abrir(self):

        log.info(f"Abriendo Excel: {self.archivo}")

        self.wb = load_workbook(self.archivo)

        self.ws = self.wb.active

    def obtener_switches(self):

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

                "password": str(password).strip()

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

        self.ws[fila][13].value = estado        # N
        self.ws[fila][14].value = falla         # O
        self.ws[fila][15].value = observacion   # P

    def guardar(self):

        self.wb.save(self.archivo)

        log.info("Excel guardado")