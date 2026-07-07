from playwright.sync_api import Page


class TrendnetSwitch:

    def __init__(self, page: Page, ip: str):

        self.page = page
        self.ip = ip

        self.csrf = None

    def open(self):

        print(f"\nAbriendo {self.ip}")

        self.page.goto(
            f"http://{self.ip}",
            wait_until="networkidle"
        )

    def get_csrf(self):

        try:

            self.csrf = self.page.locator("#csrf_token").get_attribute("value")

            print("CSRF:", self.csrf)

        except:

            print("Todavía no existe csrf_token (normal antes del login)")