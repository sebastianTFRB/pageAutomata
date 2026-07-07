from playwright.sync_api import sync_playwright


class Browser:

    def __init__(self, headless=False):
        self.headless = headless

    def __enter__(self):

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=self.headless
        )

        self.context = self.browser.new_context(
            ignore_https_errors=True
        )

        self.page = self.context.new_page()

        return self.page

    def __exit__(self, exc_type, exc_val, exc_tb):

        self.context.close()

        self.browser.close()

        self.playwright.stop()