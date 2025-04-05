# discogs/chunker.py

import re
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, BarColumn, TimeElapsedColumn, TextColumn


def sanitize_line(line: str) -> str:
    """
    Removes invalid XML characters and fixes unescaped ampersands.
    """
    line = re.sub(r'[^\x09\x0A\x0D\x20-\uD7FF\uE000-\uFFFD]', '', line)
    line = re.sub(r'&(?![a-zA-Z0-9#]+;)', '&amp;', line)
    return line


def chunk_xml_by_type(xml_file: Path, content_type: str, records_per_file: int = 10000) -> Path:
    """
    Splits a large XML file into smaller valid XML chunks.
    Returns the folder containing chunk files.
    """
    record_tag = content_type[:-1].lower()  # e.g. releases → release
    start_pat = re.compile(fr'<{record_tag}\b', re.IGNORECASE)
    end_pat = re.compile(fr'</{record_tag}>', re.IGNORECASE)

    chunk_folder = xml_file.parent / f"chunked_{content_type}"
    chunk_folder.mkdir(parents=True, exist_ok=True)

    console = Console()
    chunk_count = 0
    record_count = 0
    inside_record = False
    buffer_lines = []
    current_chunk_file = None

    def open_new_chunk():
        nonlocal chunk_count, current_chunk_file, record_count
        chunk_count += 1
        chunk_path = chunk_folder / f"chunk_{chunk_count:05}.xml"
        current_chunk_file = open(chunk_path, "w", encoding="utf-8")
        current_chunk_file.write(f'<?xml version="1.0" encoding="utf-8"?>\n<{content_type}>\n')
        record_count = 0

    def close_chunk():
        nonlocal current_chunk_file
        if current_chunk_file:
            current_chunk_file.write(f"</{content_type}>")
            current_chunk_file.close()
            current_chunk_file = None

    open_new_chunk()

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:.1f}%",
        "•",
        TimeElapsedColumn()
    ) as progress:
        task = progress.add_task(f"Chunking {xml_file.name}", total=xml_file.stat().st_size)

        with xml_file.open("r", encoding="utf-8", errors="ignore") as f:
            for raw_line in f:
                line = sanitize_line(raw_line)
                progress.update(task, advance=len(raw_line))

                if not inside_record:
                    if start_pat.search(line):
                        inside_record = True
                        buffer_lines = [line]
                else:
                    buffer_lines.append(line)
                    if end_pat.search(line):
                        current_chunk_file.write("".join(buffer_lines) + "\n")
                        record_count += 1
                        inside_record = False
                        buffer_lines = []

                        if record_count >= records_per_file:
                            close_chunk()
                            open_new_chunk()

    close_chunk()
    console.print(f"[green]✔ Chunked into {chunk_count} file(s): {chunk_folder}")
    return chunk_folder