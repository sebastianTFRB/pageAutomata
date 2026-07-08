import time


def ejecutar(log):

    log("Inicio")

    for i in range(10):

        log(f"Procesando switch {i+1}")

        time.sleep(1)

    log("Finalizado")
    