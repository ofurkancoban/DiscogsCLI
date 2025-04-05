# discogs/main.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))
import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from discogs.config import get_download_dir
from discogs.scraper import get_latest_files
from discogs.selector import select_files, select_indices, show_welcome
from discogs.downloader import download_files_threaded
from discogs.extractor import extract_gz
from discogs.chunker import chunk_xml_by_type
from discogs.converter import convert_chunks_to_csv, convert_xml_to_csv



console = Console()
app = typer.Typer(
    help="📦 Discogs CLI - Download, extract, and convert Discogs data dumps.",
    add_completion=False,
    no_args_is_help=True
)


@app.command()
def run(
    auto: bool = typer.Option(False, "--auto", "-a", help="Run in auto mode (download, extract, convert)"),
    download_dir: Path = typer.Option(None, help="Custom download directory"),
    delete_gz: bool = typer.Option(False, help="Delete .gz files after extraction"),
):
    """
    Scrape → Select → Download → Extract → Chunk → Convert
    """
    typer.echo("🔍 Fetching available Discogs files...")
    df = get_latest_files()

    if df.empty:
        typer.echo("No data found.")
        raise typer.Exit()

    selected = select_files(df)
    if not selected:
        typer.echo("No selection made.")
        raise typer.Exit()

    dest = download_dir or get_download_dir()
    dest.mkdir(parents=True, exist_ok=True)

    # Download
    downloaded = download_files_threaded(df, selected, dest)

    if not auto:
        # ❓ Extract now?
        if typer.confirm("Do you want to extract the downloaded file(s) now?", default=True):
            from discogs.extractor import extract_gz_files
            extracted = extract_gz_files(downloaded, delete_original=delete_gz)

            # ❓ Convert now?
            if typer.confirm("Do you want to convert the extracted XML files to CSV?", default=True):
                for xml_file in extracted:
                    content_type = xml_file.stem.split("_")[-1]
                    chunk_dir = chunk_xml_by_type(xml_file, content_type)
                    csv_path = xml_file.with_suffix(".csv")
                    convert_chunks_to_csv(chunk_dir, csv_path, content_type)
                typer.echo("🎉 All done!")
            else:
                typer.echo("ℹ️ You can convert later using the 'convert' command.")
        else:
            typer.echo("ℹ️ You can extract later using the 'extract' command.")
        raise typer.Exit()

    # Auto mode:
    from discogs.extractor import extract_gz_files
    extracted = extract_gz_files(downloaded, delete_original=delete_gz)
    for xml_file in extracted:
        content_type = xml_file.stem.split("_")[-1]
        chunk_dir = chunk_xml_by_type(xml_file, content_type)
        csv_path = xml_file.with_suffix(".csv")
        convert_chunks_to_csv(chunk_dir, csv_path, content_type)

    typer.echo("🎉 All done!")


@app.command()
def show():
    """
    Show available Discogs dump files.
    """
    df = get_latest_files()
    if df.empty:
        typer.echo("No files found.")
    else:
        from discogs.selector import display_table
        display_table(df)


@app.command()
def download(
    auto_extract: bool = typer.Option(False, help="Extract .gz file after download automatically"),
    auto_convert: bool = typer.Option(False, help="Convert XML to CSV after extraction"),
):
    """
    Download selected Discogs data files.
    """
    df = get_latest_files()
    if df.empty:
        typer.echo("No files found.")
        raise typer.Exit()

    indices = select_indices(df)
    if not indices:
        typer.echo("No files selected.")
        raise typer.Exit()

    download_dir = get_download_dir()
    download_dir.mkdir(parents=True, exist_ok=True)

    for i in indices:
        row = df.iloc[i]
        url = row["url"]
        downloaded_file = download_files_threaded(url, download_dir)

        if auto_extract:
            typer.echo("📦 Extracting...")
            extracted_path = extract_gz(downloaded_file)

            if auto_convert:
                typer.echo("🔄 Converting...")
                content_type = row["content"]
                convert_xml_to_csv(extracted_path, content_type)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        show_welcome()
        app(prog_name="discogs")
    else:
        app()
