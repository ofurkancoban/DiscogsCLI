# discogs/utils.py

import time
from pathlib import Path
from datetime import datetime


def human_readable_size(num_bytes: int) -> str:
    """
    Byte cinsinden bir değeri insan okunabilir formata çevirir.
    """
    if num_bytes < 1024:
        return f"{num_bytes} B"
    elif num_bytes < 1024 ** 2:
        return f"{num_bytes / 1024:.2f} KB"
    elif num_bytes < 1024 ** 3:
        return f"{num_bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{num_bytes / (1024 ** 3):.2f} GB"


def ensure_folder_exists(path: Path):
    """
    Belirtilen klasör yoksa oluşturur.
    """
    path.mkdir(parents=True, exist_ok=True)


def timestamp_now() -> str:
    """
    Şu anki zamanı Y-m-d_H-M-S formatında string olarak döner.
    """
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def wait_with_dots(seconds: int, message: str = "Waiting") -> None:
    """
    Geri sayım + noktalı bekleme efekti (CLI için hoş animasyon).
    """
    print(f"{message}", end="", flush=True)
    for _ in range(seconds):
        print(".", end="", flush=True)
        time.sleep(1)
    print("")