# discogs/selector.py

from rich.prompt import Prompt
from typing import List
import pandas as pd
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.console import Console
from discogs.utils import human_readable_size
from pathlib import Path

console = Console()


def display_table(df: pd.DataFrame) -> None:
    """
    DataFrame'deki dosyaları tablo olarak gösterir.
    """
    table = Table(title="Available Discogs Files", show_lines=True)

    table.add_column("No", style="cyan", justify="right")
    table.add_column("Month", style="magenta")
    table.add_column("Type", style="green")
    table.add_column("Size (MB)", justify="right")
    table.add_column("URL", style="dim", overflow="fold")

    for i, row in df.iterrows():
        size_mb = f"{row['size_bytes'] / (1024 ** 2):.2f}"
        table.add_row(
            str(i + 1),
            row["month"],
            row["content"],
            size_mb,
            row["url"]
        )

    console.print(table)


def select_indices(df: pd.DataFrame, allow_all: bool = False) -> List[int]:
    """
    Prompt user to select files by number (supports comma-separated list or 'all').
    """
    while True:
        selection = Prompt.ask(
            "[bold green]Select file(s) by number (comma-separated)[/]",
            default="1"
        )

        if allow_all and selection.strip().lower() == "all":
            return list(range(len(df)))

        try:
            selected = [int(x.strip()) - 1 for x in selection.split(",")]
            if all(0 <= i < len(df) for i in selected):
                return selected
            else:
                raise ValueError
        except ValueError:
            console.print("[red]Invalid selection. Try again.[/red]")


def select_files(df: pd.DataFrame) -> List[int]:
    """Kullanıcıdan dosya seçimini alır (indeks listesi döner)."""
    if df.empty:
        console.print("[red]No files to select.[/red]")
        return []

    for i, row in df.iterrows():
        size_mb = f"{row['size_bytes'] / (1024 ** 2):.2f} MB"
        console.print(f"[{i + 1}] {row['month']} | {row['content']} | {size_mb}")

    while True:
        selection = Prompt.ask("Select file(s) by number (comma-separated)", default="1")
        try:
            indices = [int(x.strip()) - 1 for x in selection.split(",")]
            if all(0 <= i < len(df) for i in indices):
                return indices
        except Exception:
            pass

        console.print("[red]Invalid selection. Try again.[/red]")



def display_status_table(df, download_dir: Path):
    table = Table(title="Available Discogs Files", show_lines=True)
    table.add_column("No", justify="right", style="cyan", no_wrap=True)
    table.add_column("Month", style="magenta")
    table.add_column("Type", style="yellow")
    table.add_column("Size", justify="right")
    table.add_column("Downloaded", justify="center")
    table.add_column("Extracted", justify="center")
    table.add_column("Converted", justify="center")

    for idx, row in df.iterrows():
        filename = Path(row["url"]).name
        year_month = row["month"]
        data_dir = download_dir / "Datasets" / year_month
        gz_path = data_dir / filename
        xml_path = gz_path.with_suffix("")
        csv_path = xml_path.with_suffix(".csv")

        is_downloaded = gz_path.exists()
        is_extracted = xml_path.exists()
        is_converted = csv_path.exists()

        check = lambda b: "[green]✔[/green]" if b else "[red]✗[/red]"

        table.add_row(
            str(idx + 1),
            row["month"],
            row["content"],
            human_readable_size(row["size_bytes"]),
            check(is_downloaded),
            check(is_extracted),
            check(is_converted),
        )

    console = Console()
    console.print(table)
def show_welcome():
    ascii_logo = r"""
        ██████╗ ██╗███████╗ ██████╗ ██████╗  ██████╗ ███████╗             
        ██╔══██╗██║██╔════╝██╔════╝██╔═══██╗██╔════╝ ██╔════╝             
        ██║  ██║██║███████╗██║     ██║   ██║██║  ███╗███████╗             
        ██║  ██║██║╚════██║██║     ██║   ██║██║   ██║╚════██║             
        ██████╔╝██║███████║╚██████╗╚██████╔╝╚██████╔╝███████║             
        ╚═════╝ ╚═╝╚══════╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝             

                    ██████╗  █████╗ ████████╗ █████╗                      
                    ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗                     
                    ██║  ██║███████║   ██║   ███████║                     
                    ██║  ██║██╔══██║   ██║   ██╔══██║                     
                    ██████╔╝██║  ██║   ██║   ██║  ██║                     
                    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝                     

██████╗ ██████╗  ██████╗  ██████╗███████╗███████╗███████╗ ██████╗ ██████╗ 
██╔══██╗██╔══██╗██╔═══██╗██╔════╝██╔════╝██╔════╝██╔════╝██╔═══██╗██╔══██╗
██████╔╝██████╔╝██║   ██║██║     █████╗  ███████╗███████╗██║   ██║██████╔╝
██╔═══╝ ██╔══██╗██║   ██║██║     ██╔══╝  ╚════██║╚════██║██║   ██║██╔══██╗
██║     ██║  ██║╚██████╔╝╚██████╗███████╗███████║███████║╚██████╔╝██║  ██║
╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚═════╝╚══════╝╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝
    """

    console.print(Panel.fit(
        ascii_logo,
        title="Discogs Data Processor CLI",
        subtitle="by ofurkancoban",
        style="bold cyan"
    ))

    md = Markdown("""
Welcome to the **Discogs CLI**!

This tool allows you to:
- 🧠 Scrape the latest data dump list from Discogs
- ⬇️  Download selected files
- 📦 Extract `.gz` files
- ✂️  Chunk large XML into smaller files
- 📄 Convert everything into tidy CSV
- 🗑 Delete downloaded/extracted/converted files
- ⚙️  Configure your download folder

---

**Available Commands:**

- `python -m discogs.main run` — Full auto mode (download → extract → convert)
- `python -m discogs.main show` — Display available Discogs files
- `python -m discogs.main download` — Download selected files (auto extract & convert)
- `python -m discogs.main extract` — Extract previously downloaded `.gz` files
- `python -m discogs.main convert` — Convert extracted `.xml` files to `.csv`
- `python -m discogs.main delete` — Delete files by selection (or `--all`)
- `python -m discogs.main config` — Set or change your download folder

---

""")
    console.print(md)