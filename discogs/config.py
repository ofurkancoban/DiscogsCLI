# discogs/config.py

import json
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt


from pathlib import Path

CONFIG_PATH = Path.home() / ".discogs_config.json"
DEFAULT_DOWNLOAD_PATH = Path.home() / "Downloads" / "Discogs"

console = Console()

def get_download_dir() -> Path:
    if CONFIG_PATH.exists():
        path = CONFIG_PATH.read_text().strip()
        if path:
            return Path(path)
    return DEFAULT_DOWNLOAD_PATH

def set_download_dir(path: str) -> None:
    CONFIG_PATH.write_text(path.strip())




def load_config() -> dict:
    """
    Loads config from disk or returns defaults.
    """
    if CONFIG_PATH.exists():
        try:
            with CONFIG_PATH.open("r") as f:
                return json.load(f)
        except Exception as e:
            console.print(f"[red]Error reading config:[/] {e}")
    return {"download_dir": str(DEFAULT_DOWNLOAD_PATH)}


def save_config(config: dict) -> None:
    """
    Saves the config to disk.
    """
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w") as f:
        json.dump(config, f, indent=4)


def get_download_dir() -> Path:
    """
    Returns configured download path, or default.
    """
    config = load_config()
    return Path(config.get("download_dir", str(DEFAULT_DOWNLOAD_PATH)))


def configure_download_folder() -> None:
    """
    CLI prompt to let user change the download directory.
    """
    console.print("[bold]Configure Discogs download folder[/bold]")
    current = get_download_dir()
    console.print(f"Current folder: [green]{current}[/green]")

    new_path = Prompt.ask("Enter new folder path or leave empty to keep current", default=str(current)).strip()
    if new_path:
        new_path = Path(new_path).expanduser()
        new_path.mkdir(parents=True, exist_ok=True)
        save_config({"download_dir": str(new_path)})
        console.print(f"[green]✅ Download folder updated to:[/] {new_path}")
    else:
        console.print("[yellow]No changes made.[/yellow]")