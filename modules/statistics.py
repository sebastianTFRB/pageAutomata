class Statistics:

    def __init__(self):

        self.total = 0
        self.actual = 0

        self.ok = 0
        self.error = 0

        self.sin_ping = 0
        self.login = 0
        self.ssh = 0
        self.guardado = 0
        self.otros = 0

    def iniciar(self, total):

        self.total = total

    def siguiente(self):

        self.actual += 1

    def mostrar_progreso(self, nombre):

        print()
        print("=" * 70)
        print(f"[{self.actual}/{self.total}] {nombre}")
        print("=" * 70)

    def resumen(self):

        print()
        print("=" * 70)
        print("RESUMEN")
        print("=" * 70)

        print(f"Total.............. {self.total}")
        print(f"Correctos.......... {self.ok}")
        print(f"Errores............ {self.error}")
        print(f"Sin Ping........... {self.sin_ping}")
        print(f"Login.............. {self.login}")
        print(f"SSH................ {self.ssh}")
        print(f"Guardar............ {self.guardado}")
        print(f"Otros.............. {self.otros}")

        print("=" * 70)