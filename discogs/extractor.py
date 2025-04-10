# discogs/extractor.py

import gzip
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TimeElapsedColumn, TextColumn

console = Console()  # Global console instance for consistent output

def extract_gz(gz_path: Path, delete_original: bool = False) -> Path:
    """
    Extracts a single .gz file into its original XML format.
    Optionally deletes the .gz file after extraction.
    """
    if gz_path.suffix != ".gz":
        raise ValueError("File is not a .gz file")

    xml_path = gz_path.with_suffix("")  # Remove ".gz" to get .xml filename
    total_size = gz_path.stat().st_size

    # Display progress bar while extracting
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        TimeElapsedColumn()
    ) as progress:
        task = progress.add_task(f"Extracting {gz_path.name}", total=total_size)

        with gzip.open(gz_path, 'rb') as f_in, open(xml_path, 'wb') as f_out:
            while True:
                chunk = f_in.read(1024 * 1024)  # Read in 1MB chunks
                if not chunk:
                    break
                f_out.write(chunk)
                progress.update(task, advance=len(chunk))

    console.print(f"[green]✔ Extracted:[/] {xml_path}")

    # Optionally remove the original .gz file after extraction
    if delete_original:
        gz_path.unlink()
        console.print(f"[yellow]🗑 Deleted original:[/] {gz_path}")

    return xml_path

def extract_gz_files(files: list[Path], delete_original: bool = False) -> list[Path]:
    """
    Extracts multiple .gz files in sequence.
    Returns a list of extracted XML file paths.
    """
    return [extract_gz(file, delete_original=delete_original) for file in files]

def get_extracted_path(gz_path: Path) -> Path:
    """
    Returns the path of the extracted XML file for a given .gz file.
    """
    return gz_path.with_suffix("")

def extract_interactively():
    """
    Prompts user to select .gz files for extraction.
    """
    from rich.prompt import Prompt
    from discogs.config import get_download_dir
    from discogs.utils import open_folder

    download_dir = get_download_dir()
    dataset_dir = download_dir / "Datasets"

    gz_files = list(dataset_dir.rglob("*.gz"))
    if not gz_files:
        console.print("[red]No .gz files found to extract.[/red]")
        return

    console.print("[bold]Select .gz file to extract:[/bold]")
    for i, file in enumerate(gz_files):
        console.print(f"[{i + 1}] {file.relative_to(download_dir)}")

    choice = Prompt.ask("Enter number", default="1")
    try:
        idx = int(choice.strip()) - 1
        if 0 <= idx < len(gz_files):
            file = gz_files[idx]
            extract_gz(file)
            open_folder(file.parent)
        else:
            console.print("[red]Invalid selection.[/red]")
    except:
        console.print("[red]Invalid input.[/red]")