# CZID Nanopore Heatmap Generator

Interactive web application for generating and visualizing heatmaps from CZID (Chan Zuckerberg ID) sample taxon reports with optional background model analysis.

## Features

- Interactive file upload for multiple CZID sample taxon report CSV files
- Background model with z-score analysis for anomaly detection
- Dynamic parameter controls for filtering and visualization
- Interactive Plotly heatmaps with zoom, pan, and hover capabilities
- Multiple metrics: bases per million (bPM), read counts, contig counts
- Advanced filtering by taxonomic level, category, thresholds, and z-scores
- Export options: PNG and CSV download
- Handles empty samples and missing data gracefully

## Usage Options

### Option 1: Web App (Easiest)

Use the hosted version directly in your browser:

**[https://ont-heatmap.streamlit.app/](https://ont-heatmap.streamlit.app/)**

No installation or setup required!

### Option 2: Local Installation

#### Prerequisites

- Python 3.8 or higher
- pip package manager

#### Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/gowtham-thakku/ont-heatmap.git
cd ont-heatmap
pip install -r requirements.txt
```

#### Running the App

```bash
streamlit run ont_heatmap_streamlit_app.py
```

The app will open automatically on your browser

## Usage

### 1. Download Data from CZID

Use the CZ ID bulk download workflow:
1. Navigate to https://czid.org/bulk_downloads
2. Download Sample Taxon Reports
3. Unzip the downloaded file

### 2. Upload Files

Click "Browse files" in the sidebar and select your CZID CSV files.

### 3. Background Model (Optional)

The background model enables detection of potential contaminants using the standard CZ ID background model approach. For details on how background models work, see the [CZ ID Background Models documentation](https://chanzuckerberg.zendesk.com/hc/en-us/articles/360050883054-Background-Models).

**Setup:**
1. Select one or more samples to use as background/control
2. Set z-score threshold (default: 0)
   - Z-score = (sample value - background mean) / background std
   - Higher values = more stringent filtering (e.g., 2 = two standard deviations above background)

### 4. Configure Parameters

**Metric** (default: nt_bpm)
- nt_bpm: Nucleotide bases per million
- nr_bpm: Protein bases per million
- Counts and contig metrics also available

**Filter Settings**
- Taxonomic Level: Species or Genus
- Categories: viruses, bacteria, archaea, eukaryota
- Threshold Filters: Minimum values for bPM and contigs

**Display Options**
- Top N taxa: Number of organisms to show per sample (1-50)
- Log transformation: Apply log(value + 1) normalization

### 5. Generate and Download

Click "Generate Heatmap" to create visualization. Download as PNG (camera icon) or CSV (download button).

## Default Configuration

```
Metric: nt_bpm
Taxonomic Level: Species
Categories: Viruses
Min NT bPM: 10
Top N taxa: 5
Log Transform: Enabled
```
## License

MIT License - see LICENSE file for details.

