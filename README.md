# 🎧 Discogs CLI — Data Processor Tool

A modern command-line tool to **download**, **extract**, and **convert** Discogs data dumps into structured CSV files.


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

### 🍻 Install with Homebrew
```bash
brew tap ofurkancoban/discogs
brew install discogs
```
### or
```bash
git clone https://github.com/ofurkancoban/DiscogsCLI.git
cd DiscogsCLI
pip install -e .
```

### 🍻 Install with Homebrew
```bash
brew tap ofurkancoban/discogs
brew install discogs
```

---

## 💻 Usage

```bash
discogs run        # Auto: download → extract → convert
discogs show       # List available Discogs data
discogs download   # Just download selected files
discogs extract    # Extract downloaded .gz files
discogs convert    # Convert extracted XML to CSV
discogs delete     # Delete files by selection or --all
discogs config     # Set download folder
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
discogs show
# [1] 2025-04 | releases | 950 MB
# [2] 2025-04 | artists  | 320 MB

discogs download
# Select 1,2
# Downloads only

discogs extract
# Select file to extract

discogs convert
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
---

Built with ❤️ by [@ofurkancoban](https://github.com/ofurkancoban)
