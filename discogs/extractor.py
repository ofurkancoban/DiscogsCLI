import gzip
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TimeElapsedColumn, TextColumn

console = Console()  # ✔ Sadece bir kez tanımla

def extract_gz(gz_path: Path, delete_original: bool = False) -> Path:
    if gz_path.suffix != ".gz":
        raise ValueError("File is not a .gz file")

    xml_path = gz_path.with_suffix("")
    total_size = gz_path.stat().st_size

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
                chunk = f_in.read(1024 * 1024)
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
    return [extract_gz(file, delete_original=delete_original) for file in files]

def get_extracted_path(gz_path: Path) -> Path:
    return gz_path.with_suffix("")