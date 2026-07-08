import threading
import flet as ft

from backend.controller import Controller


def main(page: ft.Page):

    page.title = "Trendnet SSH"

    page.window.width = 900
    page.window.height = 700

    salida = ft.TextField(
        multiline=True,
        expand=True,
        read_only=True
    )

    barra = ft.ProgressBar(
        width=700,
        value=0
    )

    controller = Controller()

    def agregar(texto):

        salida.value += texto + "\n"

        page.update()

    def ejecutar(e):

        boton.disabled = True

        page.update()

        hilo = threading.Thread(
            target=controller.ejecutar,
            args=(agregar,)
        )

        hilo.start()

    boton = ft.ElevatedButton(

        "Activar SSH",

        on_click=ejecutar

    )

    page.add(

        ft.Text(
            "Trendnet SSH Tool",
            size=28
        ),

        barra,

        boton,

        salida

    )


ft.app(target=main)