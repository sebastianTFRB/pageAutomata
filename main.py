from playwright.sync_api import sync_playwright

from modules.logger import log
from modules.excel import ExcelManager
from modules.ssh import SSHClient
from modules.trendnet import TrendnetSwitch
from modules.statistics import Statistics
from modules.timer import Timer
from modules.ping import ping


def main():

    timer = Timer()

    timer.start()

    log.info("===== INICIO DEL PROCESO =====")

    excel = ExcelManager("switches.db")

    excel.abrir()

    switches = excel.obtener_switches()

    stats = Statistics()

    stats.iniciar(len(switches))

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        for datos in switches:

            stats.siguiente()

            stats.mostrar_progreso(
                datos["nombre"]
            )

            if not ping(datos["ip"]):

                log.warning(
                    f"[{datos['ip']}] Sin respuesta al ping"
                )

                stats.error += 1
                stats.sin_ping += 1

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
                log.info(f"[{datos['ip']}] Esperando servicio SSH...")

                page.wait_for_timeout(5000)

                ssh = SSHClient(
                    datos["ip"],
                    datos["usuario"],
                    datos["password"]
                )

                ssh.connect()

                ssh.enable()

                print(
                    ssh.send("show system-info")
                )

                ssh.disconnect()
                ssh.disconnect()

                stats.ok += 1

            except Exception as e:

                texto = str(e)

                log.error(texto)

                stats.error += 1

                if "login" in texto.lower():

                    stats.login += 1

                elif "ssh" in texto.lower():

                    stats.ssh += 1

                elif "save" in texto.lower():

                    stats.guardado += 1

                else:

                    stats.otros += 1

                try:

                    page.screenshot(
                        path=f"screenshots/{datos['ip']}.png",
                        full_page=True
                    )

                except:

                    pass

            finally:

                try:

                    sw.close()

                except:

                    pass

        browser.close()

    stats.resumen()

    tiempo = timer.stop()

    print()

    print(f"Tiempo total: {tiempo} segundos")

    log.info("===== FIN DEL PROCESO =====")


if __name__ == "__main__":

    main()