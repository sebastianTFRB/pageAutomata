from time import perf_counter


class Timer:

    def __init__(self):

        self.inicio = None

    def start(self):

        self.inicio = perf_counter()

    def stop(self):

        return round(
            perf_counter() - self.inicio,
            2
        )