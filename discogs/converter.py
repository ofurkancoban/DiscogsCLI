# discogs/converter.py

import shutil
import json
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    DownloadColumn,
    TransferSpeedColumn,
)

from discogs.chunker import chunk_xml_by_type

console = Console()

def _scan_columns(chunk_file: Path, record_tag: str, column_set: set):
    """
    Scans an XML chunk file to identify all unique tag paths and attributes.
    Adds these as potential CSV columns.
    """
    current_path = []
    for event, elem in ET.iterparse(chunk_file, events=("start", "end")):
        if event == "start":
            current_path.append(elem.tag)
            # Add all attributes of the current tag to the column set
            for attr in elem.attrib:
                key = "_".join(current_path[-2:] + [attr]) if len(current_path) >= 2 else f"{elem.tag}_{attr}"
                column_set.add(key)
        elif event == "end":
            if elem.text and not elem.text.isspace():
                # Add tag path for text content
                key = "_".join(current_path[-2:] + [elem.tag]) if len(current_path) >= 2 else elem.tag
                column_set.add(key)
            current_path.pop()
            elem.clear()

def _write_rows(chunk_file: Path, writer: csv.DictWriter, columns: list, record_tag: str):
    """
    Parses an XML chunk and writes each record as a CSV row using the given column list.
    """
    current_path = []
    record_data = {}
    nested = {}

    for event, elem in ET.iterparse(chunk_file, events=("start", "end")):
        if event == "start":
            current_path.append(elem.tag)
            # Collect attribute values
            for attr, val in elem.attrib.items():
                key = "_".join(current_path[-2:] + [attr]) if len(current_path) >= 2 else f"{elem.tag}_{attr}"
                nested.setdefault(key, []).append(val)
        elif event == "end":
            if elem.text and not elem.text.isspace():
                # Collect text values
                key = "_".join(current_path[-2:] + [elem.tag]) if len(current_path) >= 2 else elem.tag
                nested.setdefault(key, []).append(elem.text.strip())

            # End of a full record → flush it to CSV
            if elem.tag == record_tag:
                for k, v in nested.items():
                    record_data[k] = v[0] if len(v) == 1 else json.dumps(v)  # Use first or serialize list
                writer.writerow({col: record_data.get(col, "") for col in columns})
                record_data.clear()
                nested.clear()

            current_path.pop()
            elem.clear()

from time import perf_counter

def convert_chunks_to_csv(chunk_dir: Path, output_csv: Path, content_type: str):
    """
    Converts all chunked XML files in a given folder into a single CSV file.
    The function discovers all columns, parses each chunk, and writes rows.
    """
    record_tag = content_type[:-1]  # e.g. "releases" → "release"
    chunks = sorted(chunk_dir.glob("chunk_*.xml"))

    if not chunks:
        console.print(f"[red]No XML chunks found in {chunk_dir}[/red]")
        return

    start_time = perf_counter()

    # Step 1: Scan all chunks to detect all column names
    column_set = set()
    console.print("[bold]Step 1:[/] Scanning tags...")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:.1f}%",
        "•",
        TimeElapsedColumn()
    ) as p:
        task = p.add_task("Scanning...", total=len(chunks))
        for chunk in chunks:
            _scan_columns(chunk, record_tag, column_set)
            p.update(task, advance=1)

    columns = sorted(column_set)

    # Step 2: Write rows into CSV
    console.print(f"[bold]Step 2:[/] Writing [green]{output_csv.name}[/green] with {len(columns)} columns...")

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:.1f}%",
            "•",
            TimeElapsedColumn()
        ) as p:
            task = p.add_task("Converting...", total=len(chunks))
            for chunk in chunks:
                _write_rows(chunk, writer, columns, record_tag)
                p.update(task, advance=1)

    duration = perf_counter() - start_time
    output_size_mb = output_csv.stat().st_size / (1024 * 1024)

    # Final status output
    console.print(f"\n[green]✔ CSV saved:[/] {output_csv}")
    console.print("[bold green]✔ Conversion completed[/bold green]")
    console.print(f"[bold white]📄 Chunks processed:[/] {len(chunks)} files")
    console.print(f"[bold white]🧩 Output CSV:[/] {output_csv.name}")
    console.print(f"[bold white]💾 Output size:[/] {output_size_mb:.2f} MB")
    console.print(f"[bold white]🗂 Saved to:[/] {output_csv.parent}")
    console.print(f"[bold white]⏱ Duration:[/] {duration:.1f} seconds")

def convert_xml_to_csv(xml_path: Path, content_type: str) -> Path:
    """
    Full pipeline: chunk an XML file and convert the chunks to a CSV file.
    Temporary chunked files are deleted after the process.
    """
    chunk_dir = xml_path.parent / f"chunked_{content_type}"
    output_csv = xml_path.with_suffix(".csv")

    chunk_xml_by_type(xml_path, content_type)  # Split large XML into smaller parts
    convert_chunks_to_csv(chunk_dir, output_csv, content_type)  # Convert chunks to CSV
    shutil.rmtree(chunk_dir, ignore_errors=True)  # Cleanup

    return output_csv

def convert_interactively():
    """
    Prompts user to select XML files for conversion.
    """
    from rich.prompt import Prompt
    from discogs.config import get_download_dir
    from discogs.utils import open_folder

    download_dir = get_download_dir()
    dataset_dir = download_dir / "Datasets"

    xml_files = list(dataset_dir.rglob("*.xml"))
    if not xml_files:
        console.print("[red]No XML files found to convert.[/red]")
        return

    console.print("[bold]Select XML file to convert:[/bold]")
    for i, file in enumerate(xml_files):
        console.print(f"[{i + 1}] {file.relative_to(download_dir)}")

    choice = Prompt.ask("Enter number", default="1")
    try:
        idx = int(choice.strip()) - 1
        if 0 <= idx < len(xml_files):
            file = xml_files[idx]
            content_type = file.stem.split("_")[-1]
            convert_xml_to_csv(file, content_type)
            open_folder(file.parent)
        else:
            console.print("[red]Invalid selection.[/red]")
    except:
        console.print("[red]Invalid input.[/red]")

__all__ = ["convert_xml_to_csv"]  # Exported symbols