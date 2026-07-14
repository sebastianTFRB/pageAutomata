import time
import paramiko

from modules.logger import log


class SSHClient:

    def __init__(self, ip, usuario, password, callback=None):

        self.ip = ip
        self.usuario = usuario
        self.password = password
        self.callback = callback

        self.transport = None
        self.channel = None

    def _emit(self, message):
        if self.callback:
            self.callback(message)

    def connect(self):

        log.info(f"[{self.ip}] Conectando por SSH...")
        self._emit(f"[{self.ip}] Conectando por SSH")

        self.transport = paramiko.Transport((self.ip, 22))

        self.transport.start_client(timeout=10)

        try:

            self.transport.auth_none(self.usuario)

            log.info(f"[{self.ip}] Autenticado mediante NONE")
            self._emit(f"[{self.ip}] Autenticado mediante NONE")

        except Exception as e:

            log.warning(
                f"[{self.ip}] auth_none falló: {e}"
            )
            self._emit(f"[{self.ip}] auth_none fallo, usando password")

            self.transport.auth_password(
                self.usuario,
                self.password
            )

            log.info(
                f"[{self.ip}] Autenticado con contraseña"
            )
            self._emit(f"[{self.ip}] Autenticado con password")

        self.channel = self.transport.open_session()

        self.channel.get_pty()

        self.channel.invoke_shell()

        time.sleep(1)

        self._leer()

        log.info(f"[{self.ip}] Consola lista")
        self._emit(f"[{self.ip}] Consola lista")

    def _leer(self):

        salida = ""

        while self.channel.recv_ready():

            datos = self.channel.recv(65535).decode(errors="ignore")

            salida += datos

        return salida

    def _es_prompt(self, texto):

        lineas = [linea.strip() for linea in (texto or "").splitlines() if linea.strip()]

        if not lineas:
            return False

        ultima = lineas[-1]

        return ultima.endswith("#") or ultima.endswith(">") or ultima.endswith("$")

    def _leer_hasta_prompt(self, timeout=30, idle=1.0):

        inicio = time.time()
        ultimo_dato = inicio
        salida = ""

        while (time.time() - inicio) < timeout:

            if self.channel.recv_ready():

                datos = self.channel.recv(65535).decode(errors="ignore")

                if datos:

                    salida += datos
                    ultimo_dato = time.time()

                    # Algunos switches paginan con "--More--" y esperan espacio.
                    if "--More--" in datos or "-- More --" in datos:
                        self.channel.send(" ")

                continue

            if salida and (time.time() - ultimo_dato) >= idle and self._es_prompt(salida):
                break

            time.sleep(0.1)

        return salida

    def send(self, comando):

        log.info(f"[{self.ip}] >> {comando}")
        self._emit(f"[{self.ip}] >> {comando}")

        self.channel.send(comando + "\n")

        salida = self._leer_hasta_prompt(timeout=40, idle=1.1)

        log.info(salida)
        if salida.strip():
            self._emit(salida.strip())

        return salida

    def enable(self):

        log.info(f"[{self.ip}] Entrando a modo enable")
        self._emit(f"[{self.ip}] Entrando a modo enable")

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
        self._emit(f"[{self.ip}] Enable correcto")

    def disconnect(self):

        if self.channel:

            self.channel.close()

        if self.transport:

            self.transport.close()

        log.info(f"[{self.ip}] SSH cerrado")
        self._emit(f"[{self.ip}] SSH cerrado")