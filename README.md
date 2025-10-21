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

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/YOUR_USERNAME/ont-heatmap.git
cd ont-heatmap
pip install -r requirements.txt
```

## Running the App

```bash
streamlit run ont_heatmap_streamlit_app.py
```

The app will open automatically at `http://localhost:8501`

## Usage

### 1. Download Data from CZID

Use the CZ ID bulk download workflow:
1. Navigate to https://czid.org/bulk_downloads
2. Download Sample Taxon Reports
3. Unzip the downloaded file

### 2. Upload Files

Click "Browse files" in the sidebar and select your CZID CSV files.

### 3. Background Model (Optional)

The background model enables statistical anomaly detection using the standard CZ ID background model approach. For details on how background models work, see the [CZ ID Background Models documentation](https://chanzuckerberg.zendesk.com/hc/en-us/articles/360050883054-Background-Models).

**Setup:**
1. Select one or more samples to use as background/control
2. Set z-score threshold (default: 0)
   - Z-score = (sample value - background mean) / background std
   - Higher values = more stringent filtering (e.g., 2 = two standard deviations above background)

**Use cases:**
- Detect pathogen outbreaks (clinical vs. healthy controls)
- Identify environmental contamination
- Find novel taxa not in background samples

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

## Expected File Format

CZID CSV files with these columns:
- `tax_id`, `tax_level`, `genus_tax_id`, `name`, `category`
- `nt_bpm`, `nr_bpm`, `nt_base_count`, `nr_base_count`
- `nt_count`, `nr_count`, `nt_contigs`, `nr_contigs`
- `nt_contig_b`, `nr_contig_b`

## Deployment

The app can be deployed to:
- **Streamlit Community Cloud** (free, recommended)
- Hugging Face Spaces
- Render, Google Cloud Run, AWS/Azure

### Quick Deploy to Streamlit Cloud

1. Push code to GitHub
2. Visit https://share.streamlit.io
3. Connect repository and deploy

## Project Structure

```
ont-heatmap/
├── ont_heatmap_streamlit_app.py  # Main Streamlit application
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── LICENSE                       # MIT License
```

## Troubleshooting

**No data after applying filters**
- Lower threshold values
- Check selected categories match your data
- Verify taxonomic level setting

**Heatmap too crowded**
- Reduce "Top N taxa" value
- Increase minimum threshold filters

**Upload fails**
- Ensure CSV format from CZID
- Verify required columns present
- Try fewer files at once

## Dependencies

- streamlit >= 1.28.0
- pandas >= 2.0.0
- numpy >= 1.24.0
- plotly >= 5.17.0

## Contributing

Contributions welcome. Please open an issue or submit a pull request.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Built with Streamlit and Plotly
- Data from CZ ID (Chan Zuckerberg ID)
- Background model based on CZ ID standard approach

## Contact

For issues or questions, please open an issue on GitHub.
