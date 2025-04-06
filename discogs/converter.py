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
    Scans a chunk file and collects unique tag paths.
    """
    current_path = []
    for event, elem in ET.iterparse(chunk_file, events=("start", "end")):
        if event == "start":
            current_path.append(elem.tag)
            for attr in elem.attrib:
                key = "_".join(current_path[-2:] + [attr]) if len(current_path) >= 2 else f"{elem.tag}_{attr}"
                column_set.add(key)
        elif event == "end":
            if elem.text and not elem.text.isspace():
                key = "_".join(current_path[-2:] + [elem.tag]) if len(current_path) >= 2 else elem.tag
                column_set.add(key)
            current_path.pop()
            elem.clear()


def _write_rows(chunk_file: Path, writer: csv.DictWriter, columns: list, record_tag: str):
    """
    Converts XML chunk into CSV rows.
    """
    current_path = []
    record_data = {}
    nested = {}

    for event, elem in ET.iterparse(chunk_file, events=("start", "end")):
        if event == "start":
            current_path.append(elem.tag)
            for attr, val in elem.attrib.items():
                key = "_".join(current_path[-2:] + [attr]) if len(current_path) >= 2 else f"{elem.tag}_{attr}"
                nested.setdefault(key, []).append(val)
        elif event == "end":
            if elem.text and not elem.text.isspace():
                key = "_".join(current_path[-2:] + [elem.tag]) if len(current_path) >= 2 else elem.tag
                nested.setdefault(key, []).append(elem.text.strip())

            if elem.tag == record_tag:
                for k, v in nested.items():
                    record_data[k] = v[0] if len(v) == 1 else json.dumps(v)
                writer.writerow({col: record_data.get(col, "") for col in columns})
                record_data.clear()
                nested.clear()

            current_path.pop()
            elem.clear()


from time import perf_counter

def convert_chunks_to_csv(chunk_dir: Path, output_csv: Path, content_type: str):
    """
    Converts all XML chunks in a directory into a single CSV file.
    """
    record_tag = content_type[:-1]
    chunks = sorted(chunk_dir.glob("chunk_*.xml"))

    if not chunks:
        console.print(f"[red]No XML chunks found in {chunk_dir}[/red]")
        return

    start_time = perf_counter()

    # Step 1: Discover columns
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

    # Step 2: Write CSV
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

    console.print(f"\n[green]✔ CSV saved:[/] {output_csv}")
    console.print("[bold green]✔ Conversion completed[/bold green]")
    console.print(f"[bold white]📄 Chunks processed:[/] {len(chunks)} files")
    console.print(f"[bold white]🧩 Output CSV:[/] {output_csv.name}")
    console.print(f"[bold white]💾 Output size:[/] {output_size_mb:.2f} MB")
    console.print(f"[bold white]🗂 Saved to:[/] {output_csv.parent}")
    console.print(f"[bold white]⏱ Duration:[/] {duration:.1f} seconds")

def convert_xml_to_csv(xml_path: Path, content_type: str) -> Path:
    chunk_dir = xml_path.parent / f"chunked_{content_type}"
    output_csv = xml_path.with_suffix(".csv")

    chunk_xml_by_type(xml_path, content_type)
    convert_chunks_to_csv(chunk_dir, output_csv, content_type)
    shutil.rmtree(chunk_dir, ignore_errors=True)

    return output_csv


__all__ = ["convert_xml_to_csv"]