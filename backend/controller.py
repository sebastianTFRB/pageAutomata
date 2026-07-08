from backend.service import TrendnetService


class Controller:

    def __init__(self):

        self.service = TrendnetService()

    def ejecutar(self, callback):

        self.service.ejecutar(callback)