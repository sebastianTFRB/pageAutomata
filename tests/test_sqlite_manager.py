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


if __name__ == "__main__":
    unittest.main()
