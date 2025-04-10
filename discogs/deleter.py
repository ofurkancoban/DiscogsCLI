# discogs/deleter.py

from pathlib import Path
from rich.console import Console
from discogs.selector import display_status_table, select_indices
from discogs.config import get_download_dir
from discogs.scraper import get_latest_files

console = Console()


def delete_files():
    """
    Interactive function that allows the user to delete selected 
    .gz, .xml, and .csv files from the dataset directory.
    """
    download_dir = get_download_dir()  # Get the base download directory from config
    df = get_latest_files()  # Load the latest file list (as a DataFrame)

    if df.empty:
        console.print("[red]No files found.[/red]")
        return

    # Show the current file status table
    display_status_table(df, download_dir)

    # Let the user select which files to delete
    selected = select_indices(df)

    for i in selected:
        row = df.iloc[i]
        filename = Path(row["url"]).name
        year_month = row["month"]
        data_dir = download_dir / "Datasets" / year_month

        gz_path = data_dir / filename  # Original .gz file
        xml_path = gz_path.with_suffix("")  # Extracted .xml file
        csv_path = xml_path.with_suffix(".csv")  # Converted .csv file

        # Try deleting each file, one by one
        for file in [gz_path, xml_path, csv_path]:
            if file.exists():
                file.unlink()  # Delete the file
                console.print(f"[red]🗑 Deleted:[/] {file.name}")
            else:
                console.print(f"[dim]• Not found:[/] {file.name}")


# Allow this script to be run directly
if __name__ == "__main__":
    delete_files()