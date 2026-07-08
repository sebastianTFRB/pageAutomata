from playwright.sync_api import sync_playwright

from modules.excel import ExcelManager
from modules.trendnet import TrendnetSwitch
from modules.ssh import SSHClient
from modules.ping import ping


class TrendnetService:

    def __init__(self):
        pass

    def ejecutar(self, callback):

        excel = ExcelManager("switches.xlsx")
        excel.abrir()

        switches = excel.obtener_switches()

        total = len(switches)

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=False
            )

            for i, datos in enumerate(switches):

                callback(
                    f"[{i+1}/{total}] {datos['nombre']}"
                )

                if not ping(datos["ip"]):

                    callback(
                        f"❌ {datos['ip']} sin respuesta"
                    )

                    continue

                page = browser.new_page()

                sw = TrendnetSwitch(
                    page,
                    datos["ip"]
                )

                try:

                    sw.open()

                    sw.login(
                        datos["usuario"],
                        datos["password"]
                    )

                    sw.enable_ssh()

                    sw.save_configuration()

                    page.wait_for_timeout(5000)

                    ssh = SSHClient(
                        datos["ip"],
                        datos["usuario"],
                        datos["password"]
                    )

                    ssh.connect()

                    ssh.enable()

                    resultado = ssh.send(
                        "show system-info"
                    )

                    callback(resultado)

                    ssh.disconnect()

                except Exception as e:

                    callback(str(e))

                finally:

                    try:
                        sw.close()
                    except:
                        pass

            browser.close()

        callback("FINALIZADO")