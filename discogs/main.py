# discogs/main.py

import typer
from discogs.selector import show_welcome, display_status_table, select_indices
from discogs.scraper import get_latest_files
from discogs.downloader import download_files_threaded
from discogs.extractor import extract_gz_files
from discogs.converter import convert_xml_to_csv
from discogs.config import get_download_dir
from discogs.utils import open_folder
from pathlib import Path
from rich.console import Console
import time

# Initialize CLI app with help text
app = typer.Typer(
    help="📦 Discogs CLI - Download, extract, and convert Discogs data dumps.",
    invoke_without_command=True
)

console = Console()

@app.command(help="One-click pipeline: Fetch latest files, download, extract, and convert to CSV.")
def run():
    """
    Full automated pipeline: shows welcome screen, fetches files,
    lets user choose which ones to download, then downloads, extracts,
    and converts them to CSV.
    """
    show_welcome()
    download_dir = get_download_dir()

    typer.echo("\U0001F50D Fetching available Discogs files...")
    df = get_latest_files()

    if df.empty:
        typer.echo("No data found.")
        raise typer.Exit()

    display_status_table(df, download_dir)
    indices = select_indices(df)

    if not indices:
        typer.echo("No selection made.")
        raise typer.Exit()

    start = time.time()

    downloaded = download_files_threaded(df, indices, download_dir)
    extracted = extract_gz_files(downloaded)

    for xml_file in extracted:
        content_type = xml_file.stem.split("_")[-1]
        convert_xml_to_csv(xml_file, content_type)

    duration = time.time() - start
    typer.secho(f"\n✅ Done in {duration:.1f} seconds!", fg="green")
    open_folder(download_dir)

@app.command()
@app.command()
def download():
    """
    Download selected Discogs data files only (no extract or convert).
    """
    download_dir = get_download_dir()
    typer.echo("\U0001F50D Fetching available Discogs files...")
    df = get_latest_files()

    if df.empty:
        typer.echo("No data found.")
        raise typer.Exit()

    display_status_table(df, download_dir)
    indices = select_indices(df)
    if not indices:
        typer.echo("No files selected.")
        raise typer.Exit()

    download_files_threaded(df, indices, download_dir)

    open_folder(download_dir)

@app.command()
def convert():
    """Convert extracted XML files to CSV (interactive mode)."""
    from discogs.converter import convert_interactively
    convert_interactively()

@app.command()
def extract():
    """Extract downloaded .gz files (interactive mode)."""
    from discogs.extractor import extract_interactively
    extract_interactively()

@app.command("delete")
def delete(all: bool = typer.Option(False, "--all", help="Delete all downloaded, extracted and converted files.")):
    """
    Deletes selected or all downloaded, extracted, and converted files.
    """
    download_dir = get_download_dir()
    df = get_latest_files()

    if df.empty:
        console.print("[red]No files found.[/red]")
        raise typer.Exit()

    display_status_table(df, download_dir)

    # If --all is passed, select all files
    selected = list(range(len(df))) if all else select_indices(df, allow_all=True)

    if not selected:
        console.print("[yellow]No files selected.[/yellow]")
        raise typer.Exit()

    for i in selected:
        row = df.iloc[i]
        year_month = row["month"]
        filename = Path(row["url"]).name
        data_dir = download_dir / "Datasets" / year_month

        gz_file = data_dir / filename
        xml_file = gz_file.with_suffix("")
        csv_file = xml_file.with_suffix(".csv")

        for file in [gz_file, xml_file, csv_file]:
            if file.exists():
                try:
                    file.unlink()
                    console.print(f"[green]✔ Deleted:[/] {file.name}")
                except Exception as e:
                    console.print(f"[red]✗ Failed to delete {file.name}:[/] {e}")
            else:
                console.print(f"[dim]• Not found:[/] {file.name}")

@app.command()
def show():
    """
    Displays the list of available Discogs dump files.
    """
    from discogs.selector import show_welcome
    from discogs.scraper import get_latest_files
    from discogs.config import get_download_dir

    show_welcome()
    df = get_latest_files()
    display_status_table(df, get_download_dir())

@app.command()
def config():
    """Launches the download folder configuration prompt."""
    from discogs.config import set_download_dir
    set_download_dir()

def entrypoint():
    import sys
    if len(sys.argv) == 1:
        app(prog_name="discogs", args=["run"])  # 👈 otomatik run
    else:
        app()

if __name__ == "__main__":
    entrypoint()