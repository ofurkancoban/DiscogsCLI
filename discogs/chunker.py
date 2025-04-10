# discogs/chunker.py

import re
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, BarColumn, TimeElapsedColumn, TextColumn


def sanitize_line(line: str) -> str:
    """
    Removes invalid XML characters and fixes unescaped ampersands.
    This helps ensure the XML is well-formed before processing.
    """
    line = re.sub(r'[^\x09\x0A\x0D\x20-\uD7FF\uE000-\uFFFD]', '', line)  # Remove illegal XML characters
    line = re.sub(r'&(?![a-zA-Z0-9#]+;)', '&amp;', line)  # Escape unescaped '&' characters
    return line


def chunk_xml_by_type(xml_file: Path, content_type: str, records_per_file: int = 10000) -> Path:
    """
    Splits a large XML file into smaller, valid XML files (chunks).
    Each chunk contains up to `records_per_file` XML records.
    Returns the folder path where chunked files are stored.
    """
    record_tag = content_type[:-1].lower()  # e.g., "releases" → "release"
    start_pat = re.compile(fr'<{record_tag}\b', re.IGNORECASE)  # Match opening tag
    end_pat = re.compile(fr'</{record_tag}>', re.IGNORECASE)    # Match closing tag

    chunk_folder = xml_file.parent / f"chunked_{content_type}"  # Output folder
    chunk_folder.mkdir(parents=True, exist_ok=True)

    console = Console()
    chunk_count = 0
    record_count = 0
    inside_record = False
    buffer_lines = []  # Stores lines of current XML record
    current_chunk_file = None

    # Helper function to open a new chunk file
    def open_new_chunk():
        nonlocal chunk_count, current_chunk_file, record_count
        chunk_count += 1
        chunk_path = chunk_folder / f"chunk_{chunk_count:05}.xml"
        current_chunk_file = open(chunk_path, "w", encoding="utf-8")
        current_chunk_file.write(f'<?xml version="1.0" encoding="utf-8"?>\n<{content_type}>\n')
        record_count = 0

    # Helper function to close the current chunk file
    def close_chunk():
        nonlocal current_chunk_file
        if current_chunk_file:
            current_chunk_file.write(f"</{content_type}>")
            current_chunk_file.close()
            current_chunk_file = None

    open_new_chunk()

    # Setup progress bar for visual feedback
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:.1f}%",
        "•",
        TimeElapsedColumn()
    ) as progress:
        task = progress.add_task(f"Chunking {xml_file.name}", total=xml_file.stat().st_size)

        # Read and process XML file line by line
        with xml_file.open("r", encoding="utf-8", errors="ignore") as f:
            for raw_line in f:
                line = sanitize_line(raw_line)
                progress.update(task, advance=len(raw_line))

                if not inside_record:
                    # Detect start of a record
                    if start_pat.search(line):
                        inside_record = True
                        buffer_lines = [line]
                else:
                    buffer_lines.append(line)
                    if end_pat.search(line):
                        # Write complete record to current chunk
                        current_chunk_file.write("".join(buffer_lines) + "\n")
                        record_count += 1
                        inside_record = False
                        buffer_lines = []

                        # If chunk is full, start a new one
                        if record_count >= records_per_file:
                            close_chunk()
                            open_new_chunk()

    close_chunk()
    console.print(f"[green]✔ Chunked into {chunk_count} file(s): {chunk_folder}")
    return chunk_folder