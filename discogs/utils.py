
import json
from rich.prompt import Prompt
from rich.console import Console
import subprocess
import platform
from pathlib import Path
console = Console()

CONFIG_PATH = Path.home() / "Downloads" / "Discogs" / ".discogs_config.json"
DEFAULT_DOWNLOAD_PATH = Path.home() / "Downloads" / "Discogs"


def load_config() -> dict:
    """
    Loads config from disk or returns defaults.
    """
    if CONFIG_PATH.exists():
        try:
            with CONFIG_PATH.open("r") as f:
                return json.load(f)
        except Exception as e:
            console.print(f"[red]⚠ Error reading config:[/] {e}")
    return {"download_dir": str(DEFAULT_DOWNLOAD_PATH)}


def save_config(config: dict):
    """
    Saves config to disk.
    """
    try:
        with CONFIG_PATH.open("w") as f:
            json.dump(config, f, indent=2)
        console.print(f"[green]✔ Config saved:[/] {CONFIG_PATH}")
    except Exception as e:
        console.print(f"[red]⚠ Failed to save config:[/] {e}")


def get_download_dir() -> Path:
    """
    Returns configured download path, or default.
    """
    config = load_config()
    return Path(config.get("download_dir", str(DEFAULT_DOWNLOAD_PATH)))



def open_folder(path: Path):
    """
    Opens the given folder path in the system's file explorer.
    """
    try:
        if platform.system() == "Darwin":  # macOS
            subprocess.run(["open", str(path)])
        elif platform.system() == "Windows":
            subprocess.run(["explorer", str(path)])
        else:  # Linux
            subprocess.run(["xdg-open", str(path)])
    except Exception as e:
        print(f"Error opening folder: {e}")
def human_readable_size(size_bytes: int) -> str:
    """
    Converts bytes to a human-readable string (e.g., KB, MB, GB).
    """
    if size_bytes == 0:
        return "0 B"

    size_name = ("B", "KB", "MB", "GB", "TB")
    i = 0
    double_size = float(size_bytes)
    while double_size >= 1024 and i < len(size_name) - 1:
        double_size /= 1024
        i += 1
    return f"{double_size:.2f} {size_name[i]}"
def set_download_dir():
    """
    Interactive prompt to change download folder.
    """
    current = get_download_dir()
    new_path = Prompt.ask("Download folder", default=str(current)).strip()
    path = Path(new_path).expanduser()

    if not path.exists():
        try:
            path.mkdir(parents=True)
            console.print(f"[green]✔ Created directory:[/] {path}")
        except Exception as e:
            console.print(f"[red]Failed to create directory:[/] {e}")
            return

    config = load_config()
    config["download_dir"] = str(path)
    save_config(config)