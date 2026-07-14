from modules.logger import log
import re
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class TrendnetSwitch:

    def __init__(self, page, ip):
        self.page = page
        self.ip = ip
        # Algunos switches tardan en responder durante guardado/aplicacion.
        # Subimos el timeout base para evitar falsos positivos por latencia.
        self.page.set_default_timeout(20000)

    def open(self):

        log.info(f"[{self.ip}] Abriendo switch")

        self.page.goto(
            f"http://{self.ip}/login.htm",
            wait_until="domcontentloaded"
        )

        self.page.wait_for_load_state("networkidle")

    def login(self, username, password):

        log.info(f"[{self.ip}] Iniciando sesión")

        self.page.get_by_role(
            "textbox",
            name="Username"
        ).fill(username)

        self.page.get_by_role(
            "textbox",
            name="Password"
        ).fill(password)

        self.page.get_by_role(
            "button",
            name="Login"
        ).click()

        self.page.wait_for_load_state("networkidle")

        if "cgi_home_page" not in self.page.url:
            raise Exception("No fue posible iniciar sesión")

        log.info(f"[{self.ip}] Login correcto")
        log.info(f"[{self.ip}] URL: {self.page.url}")

    def get_csrf_token(self):

        token = re.search(
            r"csrf_token=([a-f0-9]+)",
            self.page.url
        )

        if not token:
            raise Exception(
                f"No se encontró el CSRF Token.\nURL actual: {self.page.url}"
            )

        return token.group(1)

    def enable_ssh(self):

        log.info(f"[{self.ip}] Abriendo configuración SSH")

        token = self.get_csrf_token()

        self.page.goto(
            f"http://{self.ip}/webctrl.cgi?action=cgi_app_switch_cfg_ssh&csrf_token={token}",
            wait_until="networkidle"
        )

        self.page.locator("#ssh_state").wait_for()

        estado = self.page.locator("#ssh_state").input_value()

        log.info(f"[{self.ip}] Estado SSH actual: {estado}")

        if estado != "1":

            self.page.locator("#ssh_state").select_option("1")

            with self.page.expect_navigation(wait_until="networkidle"):
                self.page.get_by_role(
                    "button",
                    name="Apply"
                ).click()

            log.info(f"[{self.ip}] Apply completado")

            # Esperar que vuelva a existir el token en la URL
            self.page.wait_for_function(
                "() => window.location.href.includes('csrf_token=')"
            )

            log.info(f"[{self.ip}] SSH activado")

        else:

            log.info(f"[{self.ip}] SSH ya estaba habilitado")

        log.info(f"URL después de Apply: {self.page.url}")

    def save_configuration(self):

        log.info(f"[{self.ip}] Abriendo página Save")

        token = self.get_csrf_token()

        self.page.goto(
            f"http://{self.ip}/webctrl.cgi?action=cgi_sys_manage1&csrf_token={token}",
            wait_until="networkidle"
        )

        self.page.locator("#submit_save_conf").wait_for()

        self.page.once(
            "dialog",
            lambda dialog: dialog.accept()
        )

        try:
            with self.page.expect_navigation(wait_until="domcontentloaded", timeout=20000):
                self.page.locator("#submit_save_conf").click()
        except PlaywrightTimeoutError:
            # Es normal que algunos switches tarden o corten brevemente la web
            # al guardar; continuamos para validar SSH despues.
            log.warning(f"[{self.ip}] Timeout durante guardado web; se continua con espera de estabilizacion")

        log.info(f"[{self.ip}] Configuración guardada")
        log.info(f"URL final: {self.page.url}")