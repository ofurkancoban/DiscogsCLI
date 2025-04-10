# discogs/utils.py

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
    Loads the config JSON from disk.
    Returns default config if file doesn't exist or can't be read.
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
    Saves the provided config dictionary as JSON to disk.
    """
    try:
        with CONFIG_PATH.open("w") as f:
            json.dump(config, f, indent=2)
        console.print(f"[green]✔ Config saved:[/] {CONFIG_PATH}")
    except Exception as e:
        console.print(f"[red]⚠ Failed to save config:[/] {e}")

def get_download_dir() -> Path:
    """
    Returns the current download directory from config.
    Falls back to default if not configured.
    """
    config = load_config()
    return Path(config.get("download_dir", str(DEFAULT_DOWNLOAD_PATH)))

def open_folder(path: Path):
    """
    Opens the given folder path using the system's default file explorer.
    Supports macOS, Windows, and Linux.
    """
    try:
        if platform.system() == "Darwin":  # macOS
            subprocess.run(["open", str(path)])
        elif platform.system() == "Windows":
            subprocess.run(["explorer", str(path)])
        else:  # Linux (assumes xdg-open is available)
            subprocess.run(["xdg-open", str(path)])
    except Exception as e:
        print(f"Error opening folder: {e}")

def human_readable_size(size_bytes: int) -> str:
    """
    Converts a file size in bytes into a human-readable string (KB, MB, GB, etc).
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
    Prompts the user to enter a new download folder and updates the config.
    Creates the folder if it doesn't exist.
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