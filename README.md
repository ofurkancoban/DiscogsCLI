# 🎧 Discogs CLI — Data Processor Tool

A modern command-line tool to **download**, **extract**, and **convert** Discogs data dumps into structured CSV files.

Built with ❤️ by [@ofurkancoban](https://github.com/ofurkancoban)

---

## 🚀 Features

- 🧠 Scrape latest available data dump list from Discogs S3
- ⬇️ Download `.gz` files for artists, labels, releases, masters
- 📦 Extract `.gz` files to raw XML
- ✂️ Chunk large XML into smaller files
- 📄 Convert XML to clean, flat CSV files
- 🗑 Delete selected or all files
- ⚙️ Set custom download folder
- 🧪 Easy to use from terminal with friendly UI

---

## 🧩 Installation

```bash
git clone https://github.com/ofurkancoban/discogs-cli.git
cd discogs-cli
pip install -e .
```

---

## 💻 Usage

```bash
python -m discogs.main run        # Auto: download → extract → convert
python -m discogs.main show       # List available Discogs data
python -m discogs.main download   # Just download selected files
python -m discogs.main extract    # Extract downloaded .gz files
python -m discogs.main convert    # Convert extracted XML to CSV
python -m discogs.main delete     # Delete files by selection or --all
python -m discogs.main config     # Set download folder
```

---

## 📁 Folder Structure

```
~/Downloads/Discogs/
├── .discogs_config.json
└── Datasets/
    └── 2025-04/
        ├── discogs_20250401_artists.gz
        ├── discogs_20250401_artists     ← .xml
        └── discogs_20250401_artists.csv ← converted
```

---

## 🧠 Example Workflow

```bash
python -m discogs.main show
# [1] 2025-04 | releases | 950 MB
# [2] 2025-04 | artists  | 320 MB

python -m discogs.main download
# Select 1,2
# Downloads only

python -m discogs.main extract
# Select file to extract

python -m discogs.main convert
# Select XML to convert
```

---

## 🧑‍💻 Author

- GitHub: [github.com/ofurkancoban](https://github.com/ofurkancoban)
- LinkedIn: [linkedin.com/in/ofurkancoban](https://linkedin.com/in/ofurkancoban)
- Kaggle: [kaggle.com/ofurkancoban](https://www.kaggle.com/ofurkancoban)

---

## 📜 License

MIT — use freely, mention when you do something cool 😎
