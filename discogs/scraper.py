# discogs/scraper.py

import re
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from discogs.config import get_download_dir

# Base URL of the Discogs S3 bucket
S3_BASE_URL = "https://discogs-data-dumps.s3.us-west-2.amazonaws.com/"
S3_PREFIX = "data/"  # Prefix for data folders inside the bucket

def list_directories() -> list[str]:
    """
    Lists available yearly folders on the Discogs S3 bucket.
    Example: data/2024/
    """
    url = f"{S3_BASE_URL}?prefix={S3_PREFIX}&delimiter=/"
    r = requests.get(url)
    r.raise_for_status()

    ns = "{http://s3.amazonaws.com/doc/2006-03-01/}"
    root = ET.fromstring(r.text)

    dirs = []
    for cp in root.findall(ns + 'CommonPrefixes'):
        p = cp.find(ns + 'Prefix').text
        if re.match(r"data/\d{4}/", p):  # Match folders like "data/2023/"
            dirs.append(p)

    return sorted(dirs)

def list_files(directory_prefix: str) -> pd.DataFrame:
    """
    Lists files in the specified S3 folder and extracts metadata like size,
    last modified date, type (artists, labels, etc.), and generates their URLs.
    """
    url = f"{S3_BASE_URL}?prefix={directory_prefix}"
    r = requests.get(url)
    r.raise_for_status()

    ns = "{http://s3.amazonaws.com/doc/2006-03-01/}"
    root = ET.fromstring(r.text)

    data = []
    for content in root.findall(ns + 'Contents'):
        key = content.find(ns + 'Key').text
        size = int(content.find(ns + 'Size').text)
        last_modified = content.find(ns + 'LastModified').text

        # Determine content type from filename
        ctype = "unknown"
        lname = key.lower()
        if "artist" in lname:
            ctype = "artists"
        elif "label" in lname:
            ctype = "labels"
        elif "master" in lname:
            ctype = "masters"
        elif "release" in lname:
            ctype = "releases"

        # Filter only usable .gz files
        if ctype != "unknown" and key.endswith(".gz"):
            month = get_month_from_key(key)
            filename = Path(key).name
            data.append({
                "key": key,
                "size_bytes": size,
                "last_modified": last_modified,
                "month": month,
                "content": ctype,
                "filename": filename,
                "url": S3_BASE_URL + key,
            })

    df = pd.DataFrame(data)

    # Add download/extracted/converted status columns
    download_dir = get_download_dir()
    df["downloaded"] = df["filename"].apply(
        lambda fn: (download_dir / "Datasets" / get_month_from_key(fn) / fn).exists()
    )
    df["extracted"] = df["filename"].apply(
        lambda fn: (download_dir / "Datasets" / get_month_from_key(fn) / fn.replace(".gz", "")).exists()
    )
    df["converted"] = df["filename"].apply(
        lambda fn: (download_dir / "Datasets" / get_month_from_key(fn) / fn.replace(".gz", ".csv")).exists()
    )

    return df

def get_month_from_key(key: str) -> str:
    """
    Extracts the year and month from the Discogs filename.
    Example: discogs_20240101_artist.gz → 2024-01
    """
    match = re.search(r"discogs_(\d{6})\d{2}", key)
    if match:
        try:
            return datetime.strptime(match.group(1), "%Y%m").strftime("%Y-%m")
        except Exception:
            return ""
    return ""

def get_latest_files() -> pd.DataFrame:
    """
    Fetches and returns a DataFrame with files from the most recent available S3 folder.
    """
    dirs = list_directories()
    if not dirs:
        return pd.DataFrame()

    latest_dir = dirs[-1]
    df = list_files(latest_dir)

    if df.empty:
        return df

    # Parse dates and sort by month and type
    df["last_modified"] = pd.to_datetime(df["last_modified"])
    df = df.sort_values(by=["month", "content"], ascending=[False, True]).reset_index(drop=True)
    return df