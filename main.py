from playwright.sync_api import sync_playwright


import modules
from modules.trendnet import TrendnetSwitch
from modules.logger import log


def main():

    log.info("===== INICIO DEL PROCESO =====")

    excel = modules.excel.ExcelManager("switches.xlsx")

    excel.abrir()

    switches = excel.obtener_switches()

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        for datos in switches:

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

                excel.actualizar_resultado(
                    datos["fila"],
                    "OK",
                    "",
                    "SSH habilitado"
                )

            except Exception as e:

                log.error(str(e))

                excel.actualizar_resultado(
                    datos["fila"],
                    "ERROR",
                    str(e),
                    ""
                )

            finally:

                sw.close()

        browser.close()

    excel.guardar()

    log.info("===== FIN DEL PROCESO =====")


if __name__ == "__main__":

    main()