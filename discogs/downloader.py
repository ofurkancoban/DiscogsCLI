# discogs/downloader.py

import time
import requests
from time import sleep
from pathlib import Path
from urllib.parse import urlparse
from rich.console import Console
from rich.progress import (
    Progress, BarColumn, DownloadColumn, TransferSpeedColumn,
    TimeRemainingColumn, TextColumn, SpinnerColumn
)
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

console = Console()

def _download_file(url: str, target_path: Path, progress, task_id, retries: int = 5) -> Path:
    """
    Resumable and retryable file downloader with progress bar update.
    """
    headers = {}
    downloaded = 0

    if target_path.exists():
        downloaded = target_path.stat().st_size
        headers["Range"] = f"bytes={downloaded}-"

    total_size = int(requests.head(url).headers.get("Content-Length", 0))

    for attempt in range(retries):
        try:
            with requests.get(url, headers=headers, stream=True, timeout=10) as response:
                response.raise_for_status()

                mode = "ab" if downloaded else "wb"
                with open(target_path, mode) as f:
                    for chunk in response.iter_content(chunk_size=1024 * 64):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            progress.update(task_id, completed=downloaded)

            return target_path

        except requests.RequestException as e:
            if attempt < retries - 1:
                sleep(1.5)
                continue
            else:
                raise RuntimeError(f"Download failed after {retries} retries: {e}")

def download_files_threaded(df, selected_indexes, download_dir: Path) -> list[Path]:
    """
    Downloads selected files using multi-threading and shows combined progress bars.
    """
    urls = [df.iloc[i]["url"] for i in selected_indexes]
    paths = []
    total_bytes = 0
    start_time = time.time()

    with Progress(SpinnerColumn(),
        TextColumn("[progress.description]{task.description} → [bold blue]{task.fields[filename]}", justify="right"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        DownloadColumn(),
        "•",
        TransferSpeedColumn(),
        "•",
        TimeRemainingColumn(),
    ) as progress:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = []

            for url in urls:
                filename = Path(urlparse(url).path).name
                date_str = filename.split("_")[1]
                year_month = datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m")
                target_folder = download_dir / "Datasets" / year_month
                target_folder.mkdir(parents=True, exist_ok=True)
                target_path = target_folder / filename

                if target_path.exists():
                    console.print(f"[yellow]⚠ Already downloaded:[/] {filename}")
                    paths.append(target_path)
                    continue

                total = int(requests.head(url).headers.get("Content-Length", 0))
                total_bytes += total
                task_id = progress.add_task("Downloading", filename=filename, total=total)
                future = executor.submit(_download_file, url, target_path, progress, task_id)
                futures.append(future)

            for future in as_completed(futures):
                try:
                    result = future.result()
                    paths.append(result)
                except Exception as e:
                    console.print(f"[red]Error downloading file:[/] {e}")

    duration = time.time() - start_time
    size_mb = total_bytes / (1024 ** 2)

    console.print(f"\n[green]📥 {len(paths)} file(s) downloaded[/]")
    console.print(f"[cyan]💾 Total size:[/] {size_mb:.1f} MB")
    console.print(f"[cyan]⏱ Duration:[/] {duration:.1f} seconds")

    return paths
