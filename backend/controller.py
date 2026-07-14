from backend.service import TrendnetService
from backend.ssh_commands_service import SSHCommandsService


class Controller:

    def __init__(self):

        self.service = TrendnetService()
        self.ssh_commands_service = SSHCommandsService()

    def ejecutar(self, callback):

        # Mantener compatibilidad con llamadas existentes.
        self.ejecutar_activacion_ssh(callback)

    def ejecutar_activacion_ssh(self, callback, selected_ids=None):

        self.service.ejecutar(callback, selected_ids=selected_ids)

    def ejecutar_ssh_commands(self, callback, comandos):

        self.ssh_commands_service.ejecutar(callback, comandos)