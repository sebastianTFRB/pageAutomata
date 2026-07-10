import csv
import os
import tempfile
import unittest

from backend.service import TrendnetService
from modules.excel import ExcelManager


class SQLiteManagerTests(unittest.TestCase):

    def test_summary_message_contains_basic_counts(self):
        service = TrendnetService()
        service.estadisticas = {
            "total": 5,
            "con_ping": 3,
            "sin_ping": 2,
            "exitosos": 2,
            "fallos": 1,
            "errores_login": 1,
            "errores_ssh": 0,
            "errores_guardado": 0,
            "errores_otros": 0,
        }

        resumen = service.obtener_resumen_texto()

        self.assertIn("Total: 5", resumen)
        self.assertIn("Con ping: 3", resumen)
        self.assertIn("Sin ping: 2", resumen)
        self.assertIn("Fallos: 1", resumen)

    def test_import_from_csv_and_export_to_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "switches.db")
            csv_path = os.path.join(tmpdir, "switches.csv")
            export_path = os.path.join(tmpdir, "export.csv")

            with open(csv_path, "w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["nombre", "ip", "usuario", "password", "zona", "estado", "ssh", "fecha"],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "nombre": "Switch A",
                        "ip": "192.168.1.1",
                        "usuario": "admin",
                        "password": "secret",
                        "zona": "Core",
                        "estado": "en funcionamiento",
                        "ssh": "habilitado",
                        "fecha": "2026-07-08",
                    }
                )

            manager = ExcelManager(db_path)
            manager.abrir()
            manager.importar_desde_csv(csv_path)

            switches = manager.obtener_switches()

            self.assertEqual(len(switches), 1)
            self.assertEqual(switches[0]["nombre"], "Switch A")
            self.assertEqual(switches[0]["ip"], "192.168.1.1")

            manager.exportar_csv(export_path)

            with open(export_path, newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["nombre"], "Switch A")

    def test_generic_device_types_can_be_filtered(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "switches.db")

            manager = ExcelManager(db_path)
            manager.abrir()
            manager.agregar_dispositivo(
                tipo="switch",
                nombre="Switch Core",
                ip="192.168.1.10",
                usuario="admin",
                password="secret",
            )
            manager.agregar_dispositivo(
                tipo="camara",
                nombre="Camara 1",
                ip="192.168.1.20",
                usuario="admin",
                password="secret",
            )
            manager.agregar_dispositivo(
                tipo="workstation",
                nombre="PC 1",
                ip="192.168.1.30",
                usuario="user",
                password="secret",
            )

            todos = manager.obtener_dispositivos()
            switches = manager.obtener_switches()
            camaras = manager.obtener_dispositivos("camara")

            self.assertEqual(len(todos), 3)
            self.assertEqual(len(switches), 1)
            self.assertEqual(switches[0]["nombre"], "Switch Core")
            self.assertEqual(len(camaras), 1)
            self.assertEqual(camaras[0]["nombre"], "Camara 1")

    def test_import_without_tipo_uses_default_type(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "switches.db")
            csv_path = os.path.join(tmpdir, "camaras.csv")

            with open(csv_path, "w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["nombre", "ip", "usuario", "password", "estado", "ssh", "fecha"],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "nombre": "Camara Patio",
                        "ip": "192.168.2.10",
                        "usuario": "admin",
                        "password": "secret",
                        "estado": "en funcionamiento",
                        "ssh": "false",
                        "fecha": "2026-07-09",
                    }
                )

            manager = ExcelManager(db_path)
            manager.abrir()
            manager.importar_desde_archivo(csv_path, tipo_default="camara")

            camaras = manager.obtener_dispositivos("camara")
            switches = manager.obtener_switches()

            self.assertEqual(len(camaras), 1)
            self.assertEqual(camaras[0]["nombre"], "Camara Patio")
            self.assertEqual(len(switches), 0)


if __name__ == "__main__":
    unittest.main()
