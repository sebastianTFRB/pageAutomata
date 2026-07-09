import os
from datetime import datetime

from modules.excel import ExcelManager
from modules.ssh import SSHClient


class SSHCommandsService:
    def __init__(self):
        self.estadisticas = {}

    def _reset_stats(self):
        self.estadisticas = {
            "total": 0,
            "inactivos_omitidos": 0,
            "procesados": 0,
            "exitosos": 0,
            "fallos": 0,
            "sin_credenciales": 0,
            "sin_ip": 0,
        }

    def _resumen(self):
        return (
            "Resumen final SSH Commands\n"
            f"Total: {self.estadisticas['total']}\n"
            f"Inactivos omitidos: {self.estadisticas['inactivos_omitidos']}\n"
            f"Procesados: {self.estadisticas['procesados']}\n"
            f"Exitosos: {self.estadisticas['exitosos']}\n"
            f"Fallos: {self.estadisticas['fallos']}\n"
            f"Sin IP: {self.estadisticas['sin_ip']}\n"
            f"Sin credenciales: {self.estadisticas['sin_credenciales']}"
        )

    def _safe_filename(self, value: str) -> str:
        safe = "".join(ch if ch.isalnum() or ch in "-_ ." else "_" for ch in value)
        return safe.strip() or "switch"

    def ejecutar(self, callback, comandos):
        self._reset_stats()

        comandos_limpios = [str(c).strip() for c in (comandos or []) if str(c).strip()]
        if not comandos_limpios:
            callback("ERROR: Debes seleccionar o escribir al menos un comando")
            callback(self._resumen())
            return

        db = ExcelManager("switches.db")
        db.abrir()
        switches = db.obtener_switches()

        # Solo se intentan conexiones SSH sobre switches activos/funcionando.
        estados_validos = {"funcionando", "en funcionamiento"}
        switches_elegibles = [
            sw for sw in switches
            if (sw.get("estado") or "").strip().lower() in estados_validos
        ]

        self.estadisticas["total"] = len(switches_elegibles)
        self.estadisticas["inactivos_omitidos"] = len(switches) - len(switches_elegibles)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join("backups", f"ssh_commands_{timestamp}")
        os.makedirs(backup_dir, exist_ok=True)

        callback("Iniciando proceso SSH Commands")
        callback(f"Switches activos para procesar: {self.estadisticas['total']}")
        if self.estadisticas["inactivos_omitidos"] > 0:
            callback(f"Switches inactivos omitidos: {self.estadisticas['inactivos_omitidos']}")
        callback(f"Comandos a ejecutar: {len(comandos_limpios)}")
        for cmd in comandos_limpios:
            callback(f" - {cmd}")

        for idx, sw in enumerate(switches_elegibles, start=1):
            nombre = (sw.get("nombre") or "").strip() or f"switch_{idx}"
            ip = (sw.get("ip") or "").strip()
            usuario = (sw.get("usuario") or "").strip()
            password = (sw.get("password") or "").strip()

            callback(f"[{idx}/{self.estadisticas['total']}] {nombre} ({ip or 'sin-ip'})")

            if not ip:
                self.estadisticas["sin_ip"] += 1
                self.estadisticas["fallos"] += 1
                callback(f"SKIP {nombre}: sin IP")
                continue

            if not usuario or not password:
                self.estadisticas["sin_credenciales"] += 1
                self.estadisticas["fallos"] += 1
                callback(f"SKIP {nombre}: sin usuario/password")
                continue

            self.estadisticas["procesados"] += 1

            ssh = SSHClient(ip, usuario, password, callback=callback)
            salida_total = ""

            try:
                ssh.connect()
                ssh.enable()

                for comando in comandos_limpios:
                    callback(f"CMD [{ip}] {comando}")
                    salida = ssh.send(comando)

                    salida_total += "\n"
                    salida_total += "=" * 80 + "\n"
                    salida_total += comando + "\n"
                    salida_total += "=" * 80 + "\n\n"
                    salida_total += (salida or "")
                    salida_total += "\n\n"

                archivo = os.path.join(backup_dir, f"{self._safe_filename(nombre)}.txt")
                with open(archivo, "w", encoding="utf-8") as f:
                    f.write(salida_total)

                self.estadisticas["exitosos"] += 1
                callback(f"OK {nombre}: respaldo guardado en {archivo}")

            except Exception as ex:
                self.estadisticas["fallos"] += 1
                callback(f"ERROR {nombre}: {ex}")
            finally:
                try:
                    ssh.disconnect()
                except Exception:
                    pass

        callback("FINALIZADO SSH Commands")
        callback(self._resumen())
