from playwright.sync_api import sync_playwright

from modules.excel import ExcelManager
from modules.trendnet import TrendnetSwitch
from modules.ssh import SSHClient
from modules.ping import ping


class TrendnetService:

    def __init__(self):
        self.estadisticas = {
            "total": 0,
            "con_ping": 0,
            "sin_ping": 0,
            "exitosos": 0,
            "fallos": 0,
            "errores_login": 0,
            "errores_ssh": 0,
            "errores_guardado": 0,
            "errores_otros": 0,
        }

    def obtener_resumen_texto(self):

        return (
            "Resumen final\n"
            f"Total: {self.estadisticas['total']}\n"
            f"Con ping: {self.estadisticas['con_ping']}\n"
            f"Sin ping: {self.estadisticas['sin_ping']}\n"
            f"Exitosos: {self.estadisticas['exitosos']}\n"
            f"Fallos: {self.estadisticas['fallos']}\n"
            f"Errores login: {self.estadisticas['errores_login']}\n"
            f"Errores SSH: {self.estadisticas['errores_ssh']}\n"
            f"Errores guardado: {self.estadisticas['errores_guardado']}\n"
            f"Errores otros: {self.estadisticas['errores_otros']}"
        )

    def ejecutar(self, callback):

        # Reiniciar contadores para cada ejecucion
        self.estadisticas = {
            "total": 0,
            "con_ping": 0,
            "sin_ping": 0,
            "exitosos": 0,
            "fallos": 0,
            "errores_login": 0,
            "errores_ssh": 0,
            "errores_guardado": 0,
            "errores_otros": 0,
        }

        excel = ExcelManager("switches.db")
        excel.abrir()

        switches = excel.obtener_switches()

        self.estadisticas["total"] = len(switches)

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=False
            )

            callback("Iniciando navegador y flujo de automatizacion")

            for i, datos in enumerate(switches):

                callback(
                    f"[{i+1}/{self.estadisticas['total']}] Procesando {datos['nombre']}"
                )
                callback(f"PING {datos['ip']} ...")

                if not ping(datos["ip"]):

                    self.estadisticas["sin_ping"] += 1
                    self.estadisticas["fallos"] += 1
                    callback(f"SKIP {datos['nombre']}: sin respuesta de ping")
                    continue

                self.estadisticas["con_ping"] += 1

                page = browser.new_page()

                sw = TrendnetSwitch(
                    page,
                    datos["ip"]
                )

                try:

                    callback(f"[{datos['ip']}] Abriendo interfaz web")

                    sw.open()

                    callback(f"[{datos['ip']}] Login web")

                    sw.login(
                        datos["usuario"],
                        datos["password"]
                    )

                    callback(f"[{datos['ip']}] Activando SSH en web")

                    sw.enable_ssh()

                    callback(f"[{datos['ip']}] Guardando configuracion")

                    sw.save_configuration()

                    callback(f"[{datos['ip']}] Esperando servicio SSH")

                    page.wait_for_timeout(5000)

                    ssh = SSHClient(
                        datos["ip"],
                        datos["usuario"],
                        datos["password"],
                        callback=callback,
                    )

                    ssh.connect()

                    ssh.enable()

                    callback(f"CMD [{datos['ip']}] show system-info")
                    salida_cmd = ssh.send(
                        "show system-info"
                    )

                    salida_limpia = (salida_cmd or "").strip()
                    if salida_limpia:
                        callback(salida_limpia)

                    self.estadisticas["exitosos"] += 1
                    callback(f"OK {datos['nombre']} completado")

                    ssh.disconnect()

                except Exception as e:

                    self.estadisticas["fallos"] += 1
                    texto = str(e).lower()
                    callback(f"ERROR {datos['nombre']}: {str(e)}")

                    if "login" in texto:
                        self.estadisticas["errores_login"] += 1
                    elif "ssh" in texto:
                        self.estadisticas["errores_ssh"] += 1
                    elif "save" in texto:
                        self.estadisticas["errores_guardado"] += 1
                    else:
                        self.estadisticas["errores_otros"] += 1

                finally:

                    try:
                        sw.close()
                    except:
                        pass

            browser.close()

        callback("FINALIZADO")
        callback(self.obtener_resumen_texto())