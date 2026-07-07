import subprocess
import platform


def ping(ip):

    if platform.system().lower() == "windows":

        comando = [
            "ping",
            "-n",
            "1",
            "-w",
            "1000",
            ip
        ]

    else:

        comando = [
            "ping",
            "-c",
            "1",
            "-W",
            "1",
            ip
        ]

    resultado = subprocess.run(

        comando,

        stdout=subprocess.DEVNULL,

        stderr=subprocess.DEVNULL

    )

    return resultado.returncode == 0