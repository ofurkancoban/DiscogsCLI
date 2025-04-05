# discogs/downloader.py
import requests
from pathlib import Path
from urllib.parse import urlparse
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
)
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

console = Console()


def _download_file(url: str, target_path: Path, progress, task_id) -> Path:
    response = requests.get(url, stream=True)
    with open(target_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024 * 64):
            if chunk:
                f.write(chunk)
                progress.update(task_id, advance=len(chunk))
    return target_path


def download_files_threaded(df, selected_indexes, download_dir: Path) -> list[Path]:
    """
    Downloads selected files using multi-threading and shows combined progress bars.
    """
    urls = [df.iloc[i]["url"] for i in selected_indexes]
    paths = []

    with Progress(
        SpinnerColumn(),  # 👈 Dönen yılan efekti
        TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        DownloadColumn(),
        "•",
        TransferSpeedColumn(),
        "•",
        TimeRemainingColumn(),
        console=console,
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

                total = int(requests.head(url).headers.get("Content-Length", 0))
                task_id = progress.add_task("Downloading", filename=filename, total=total)
                future = executor.submit(_download_file, url, target_path, progress, task_id)
                futures.append(future)

            for future in as_completed(futures):
                try:
                    result = future.result()
                    paths.append(result)
                except Exception as e:
                    console.print(f"[red]Error downloading file:[/] {e}")

    return paths