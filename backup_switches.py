import os
import time
import paramiko


SWITCHES = [
    {
        "nombre": "SW14-FIGUEROA",
        "ip": "172.16.0.133"
    },
    {
        "nombre": "SW17-POLVORIN",
        "ip": "172.16.0.137"
    },
    {
        "nombre": "SW90-COM. PARQUE INFANTIL",
        "ip": "172.16.0.190"
    },
    {
        "nombre": "SW88-HOSPITAL CIVIL",
        "ip": "172.16.0.188"
    },
    {
        "nombre": "SW91 / 92 SALIDA NORTE CHAPULTEPEC",
        "ip": "172.16.0.191"
    },
    {
        "nombre": "SW89-LA COLINA",
        "ip": "172.16.0.189"
    },
    {
        "nombre": "SW99- PEDAGOGICO",
        "ip": "172.16.0.195"
    },
    {
        "nombre": "SW37-JESUS POLIDEPORTIVO",
        "ip": "172.16.0.155"
    },
    {
        "nombre": "SW54-QUINTAS DE SAN PEDRO",
        "ip": "172.16.0.172"
    },
    {
        "nombre": "SW39-PANDIACO",
        "ip": "172.16.0.157"
    },
    {
        "nombre": "SW38-SOL DE ORIENTE",
        "ip": "172.16.0.156"
    },
    {
        "nombre": "SW05-CIUDAD REAL",
        "ip": "172.16.0.124"
    },
    {
        "nombre": "SW59-UDENAR",
        "ip": "172.16.0.171"
    },
    {
        "nombre": "SW42-CLINICA LAS AMERICAS",
        "ip": "172.16.0.160"
    },
    {
        "nombre": "SW60-PARQUEADERO VILLANUEVA",
        "ip": "172.16.0.173"
    },
    {
        "nombre": "SW73-INTERCAMBIADOR VILLANUEVA",
        "ip": "172.16.0.182"
    },
    {
        "nombre": "SW74-U. COOPERATIVA",
        "ip": "172.16.0.183"
    },
    
    # Agrega aquí los demás...
]


USUARIO = "admin"
PASSWORD_ENABLE = "P@sto2025"


COMANDOS = [
    "show spanning-tree active"
]


os.makedirs("backups", exist_ok=True)


def esperar_prompt(shell, prompt="#", timeout=10):

    salida = ""
    inicio = time.time()

    while time.time() - inicio < timeout:

        if shell.recv_ready():

            datos = shell.recv(65535).decode(errors="ignore")

            salida += datos

            if prompt in salida:
                break

        time.sleep(0.2)

    return salida


for sw in SWITCHES:

    print(f"\n===== {sw['nombre']} =====")

    try:

        cliente = paramiko.SSHClient()
        cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        transporte = paramiko.Transport((sw["ip"], 22))

        transporte.start_client(timeout=10)

        transporte.auth_none(USUARIO)

        canal = transporte.open_session()
        canal.get_pty()
        canal.invoke_shell()

        esperar_prompt(canal, ">")

        canal.send("enable\n")
        esperar_prompt(canal, "user:")

        canal.send(USUARIO + "\n")
        esperar_prompt(canal, "password:")

        canal.send(PASSWORD_ENABLE + "\n")
        esperar_prompt(canal, "#")

        salida_total = ""

        for comando in COMANDOS:

            print(f"  Ejecutando {comando}")

            canal.send(comando + "\n")

            salida = esperar_prompt(canal, "#", timeout=20)

            salida_total += "\n"
            salida_total += "=" * 80 + "\n"
            salida_total += comando + "\n"
            salida_total += "=" * 80 + "\n\n"
            salida_total += salida
            salida_total += "\n\n"

        archivo = os.path.join(
            "backups",
            f"{sw['nombre']}.txt"
        )

        with open(
            archivo,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(salida_total)

        print("OK")

        canal.close()
        transporte.close()

    except Exception as e:

        print(f"ERROR: {e}")