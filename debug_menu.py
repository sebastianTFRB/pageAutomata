from playwright.sync_api import sync_playwright

IP = "172.16.0.170"
USER = "admin"
PASSWORD = "P@sto2025"


with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    page.goto(f"http://{IP}/login.htm")

    page.get_by_role("textbox", name="Username").fill(USER)
    page.get_by_role("textbox", name="Password").fill(PASSWORD)
    page.get_by_role("button", name="Login").click()

    page.wait_for_load_state("networkidle")

    tree = page.frame(name="tree")

    print("=" * 80)
    print("ENLACES ENCONTRADOS")
    print("=" * 80)

    links = tree.locator("a")

    total = links.count()

    print(f"Total de enlaces: {total}")
    print()

    for i in range(total):

        link = links.nth(i)

        try:
            texto = link.inner_text(timeout=1000).strip()
        except:
            texto = ""

        href = link.get_attribute("href")

        print(f"[{i}]")
        print(f"Texto : {texto}")
        print(f"Href  : {href}")
        print("-" * 80)

    input("\nPresiona ENTER para cerrar...")

    browser.close()