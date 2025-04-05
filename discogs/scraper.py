# discogs/scraper.py

import re
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime

S3_BASE_URL = "https://discogs-data-dumps.s3.us-west-2.amazonaws.com/"
S3_PREFIX = "data/"


def list_directories() -> list[str]:
    """
    S3 üzerinden yıllık klasörleri listeler (örnek: data/2024/)
    """
    url = f"{S3_BASE_URL}?prefix={S3_PREFIX}&delimiter=/"
    r = requests.get(url)
    r.raise_for_status()

    ns = "{http://s3.amazonaws.com/doc/2006-03-01/}"
    root = ET.fromstring(r.text)

    dirs = []
    for cp in root.findall(ns + 'CommonPrefixes'):
        p = cp.find(ns + 'Prefix').text
        if re.match(r"data/\d{4}/", p):
            dirs.append(p)
    return sorted(dirs)


def list_files(directory_prefix: str) -> pd.DataFrame:
    """
    Verilen dizindeki dosyaları listeler ve metaverilerini çıkartır.
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

        if ctype != "unknown" and key.endswith(".gz"):
            data.append({
                "key": key,
                "size_bytes": size,
                "last_modified": last_modified,
                "month": get_month_from_key(key),
                "content": ctype,
                "url": S3_BASE_URL + key,
            })

    return pd.DataFrame(data)


def get_month_from_key(key: str) -> str:
    """
    Örnek key'den ay bilgisi çıkarır (discogs_20240101_artist → 2024-01)
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
    En güncel dizindeki verileri indirip döner.
    """
    dirs = list_directories()
    if not dirs:
        return pd.DataFrame()

    latest_dir = dirs[-1]
    df = list_files(latest_dir)

    if df.empty:
        return df

    df["last_modified"] = pd.to_datetime(df["last_modified"])
    df = df.sort_values(by=["month", "content"], ascending=[False, True]).reset_index(drop=True)
    return df