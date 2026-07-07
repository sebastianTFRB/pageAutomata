import time
import paramiko

from modules.logger import log


class SSHClient:

    def __init__(self, ip, usuario, password):

        self.ip = ip
        self.usuario = usuario
        self.password = password

        self.transport = None
        self.channel = None

    def connect(self):

        log.info(f"[{self.ip}] Conectando por SSH...")

        self.transport = paramiko.Transport((self.ip, 22))

        self.transport.start_client(timeout=10)

        try:

            self.transport.auth_none(self.usuario)

            log.info(f"[{self.ip}] Autenticado mediante NONE")

        except Exception as e:

            log.warning(
                f"[{self.ip}] auth_none falló: {e}"
            )

            self.transport.auth_password(
                self.usuario,
                self.password
            )

            log.info(
                f"[{self.ip}] Autenticado con contraseña"
            )

        self.channel = self.transport.open_session()

        self.channel.get_pty()

        self.channel.invoke_shell()

        time.sleep(1)

        self._leer()

        log.info(f"[{self.ip}] Consola lista")

    def _leer(self):

        salida = ""

        while self.channel.recv_ready():

            datos = self.channel.recv(65535).decode(errors="ignore")

            print(repr(datos))

            salida += datos

        return salida

    def send(self, comando):

        log.info(f"[{self.ip}] >> {comando}")

        self.channel.send(comando + "\n")

        time.sleep(1)

        salida = self._leer()

        log.info(salida)

        return salida

    def enable(self):

        log.info(f"[{self.ip}] Entrando a modo enable")

        self.channel.send("enable\n")

        salida = ""

        for _ in range(20):

            time.sleep(0.5)

            salida += self._leer()

            if "user:" in salida.lower():
                break

        log.info(salida)

        if "user:" not in salida.lower():
            raise Exception("El switch nunca pidió el usuario")

        self.channel.send(self.usuario + "\n")

        salida = ""

        for _ in range(20):

            time.sleep(0.5)

            salida += self._leer()

            if "password:" in salida.lower():
                break

        log.info(salida)

        self.channel.send(self.password + "\n")

        salida = ""

        for _ in range(20):

            time.sleep(0.5)

            salida += self._leer()

            if "#" in salida:
                break

        log.info(salida)

        if "#" not in salida:
            raise Exception("No fue posible entrar en modo enable")

        log.info(f"[{self.ip}] Enable correcto")

    def disconnect(self):

        if self.channel:

            self.channel.close()

        if self.transport:

            self.transport.close()

        log.info(f"[{self.ip}] SSH cerrado")