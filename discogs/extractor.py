# discogs/extractor.py

import gzip
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TimeElapsedColumn, TextColumn

console = Console()

import gzip
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

def extract_gz(gz_path: Path, delete_original: bool = False) -> Path:
    """
    Extracts a .gz file to .xml in the same directory.
    If delete_original=True, removes the original .gz after extraction.
    """
    if gz_path.suffix != ".gz":
        raise ValueError("File is not a .gz file")

    xml_path = gz_path.with_suffix("")  # removes ".gz"
    total_size = gz_path.stat().st_size

    console = Console()
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
                chunk = f_in.read(1024 * 1024)  # 1MB
                if not chunk:
                    break
                f_out.write(chunk)
                progress.update(task, advance=len(chunk))

    console.print(f"[green]✔ Extracted:[/] {xml_path}")

    if delete_original:
        gz_path.unlink()
        console.print(f"[yellow]🗑 Deleted original:[/] {gz_path}")

    return xml_path

def extract_gz_files(files: list[Path], delete_original: bool = False) -> list[Path]:
    """
    Takes a list of .gz files and extracts them.
    Returns a list of .xml file paths.
    """
    extracted = []
    for file in files:
        extracted_file = extract_gz(file, delete_original=delete_original)
        extracted.append(extracted_file)
    return extracted