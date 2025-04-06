# discogs/deleter.py

from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm
from discogs.selector import display_status_table, select_indices
from discogs.config import get_download_dir
from discogs.scraper import get_latest_files

console = Console()


def delete_files():
    """
    Interactive deletion of selected .gz, .xml, and .csv files.
    """
    download_dir = get_download_dir()
    df = get_latest_files()

    if df.empty:
        console.print("[red]No files found.[/red]")
        return

    display_status_table(df, download_dir)
    selected = select_indices(df)

    for i in selected:
        row = df.iloc[i]
        filename = Path(row["url"]).name
        year_month = row["month"]
        data_dir = download_dir / "Datasets" / year_month

        gz_path = data_dir / filename
        xml_path = gz_path.with_suffix("")
        csv_path = xml_path.with_suffix(".csv")

        for file in [gz_path, xml_path, csv_path]:
            if file.exists():
                file.unlink()
                console.print(f"[red]🗑 Deleted:[/] {file.name}")
            else:
                console.print(f"[dim]• Not found:[/] {file.name}")


if __name__ == "__main__":
    delete_files()
