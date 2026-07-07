import logging
from pathlib import Path

Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(
            "logs/trendnet.log",
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)

log = logging.getLogger("Trendnet")