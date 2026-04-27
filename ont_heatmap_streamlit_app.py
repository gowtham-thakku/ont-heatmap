import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO
import tempfile
import os

st.set_page_config(page_title="CZID Nanopore Heatmap Generator", layout="wide")

# Title and description
st.title("CZID Nanopore Heatmap Generator")
st.markdown("""
Upload your CZID sample taxon reports to generate an interactive heatmap.
Adjust parameters in the sidebar to customize your visualization.
""")

# Helper functions
def read_czid_report(file_content, filename,
                     metric='nt_bpm',
                     tax_level=[],
                     category_list=[],
                     min_nt_bpm=1,
                     min_nr_bpm=1,
                     min_nt_contigs=0,
                     min_nr_contigs=0,
                     min_nt_count=0):
    """
    Read in the CZ ID Sample Taxon Reports, applying filtering.
    Conservative default filter values are provided, but filters may be adjusted when calling the function.
    Returns (df, samplename) tuple. Returns (None, None) if file is invalid/empty.
    Returns (empty_df, samplename) if file is valid but has no data after filtering.
    """

    try:
        file_content.seek(0)
        df = pd.read_csv(file_content)

        # Extract sample name first
        samplename = '_'.join(filename.split('_')[0:-3])

        # Check if dataframe is empty or has no rows
        if df.empty or len(df) == 0:
            return None, None

        df.fillna(0, inplace=True)

        # Check if required columns exist
        required_cols = ['tax_level', 'category', 'nt_bpm', 'nr_bpm', 'nt_contig_b', 'nr_contig_b', 'nt_count', 'name']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.warning(f"File '{filename}' is missing columns: {missing_cols}. Skipping.")
            return None, None

        # filter on tax_level
        if len(tax_level) > 0:
            df = df.loc[df['tax_level'].isin(tax_level)]

        # select only categories of interest
        if len(category_list) > 0:
            df = df.loc[df['category'].isin(category_list)]

        # apply filters on specific data columns
        df = df[df['nt_bpm'] >= min_nt_bpm]           # min_nt_bpm
        df = df[df['nr_bpm'] >= min_nr_bpm]           # min_nr_bpm
        df = df[df['nt_contig_b'] >= min_nt_contigs]  # min_nt_contigs
        df = df[df['nr_contig_b'] >= min_nr_contigs]  # min_nr_contigs
        df = df[df['nt_count'] >= min_nt_count]        # min_nt_count

        # add samplename column to enable concatenating dataframes to long format
        df['samplename'] = samplename

        # Return the df and samplename, even if df is empty after filtering
        return df, samplename

    except Exception as e:
        st.warning(f"Could not parse '{filename}': {e}")
        return None, None


def extract_sample_name(filename):
    """
    Extract sample name from CZID filename
    """
    return '_'.join(filename.split('_')[0:-3])


def calculate_z_scores(df, background_samples, metric='nt_bpm'):
    """
    Calculate z-scores for each taxon-sample pair based on background model.
    Z-scores are bounded between -100 and 100.

    Parameters:
    -----------
    df : DataFrame
        Long format dataframe with columns: name, samplename, metric, etc.
    background_samples : list
        List of sample names to use as background
    metric : str
        The metric to use for z-score calculation (default: 'nt_bpm')

    Returns:
    --------
    DataFrame with additional 'z_score' column
    """
    # Filter background samples
    background_df = df[df['samplename'].isin(background_samples)]

    # Calculate mean and std for each taxon in background
    background_stats = background_df.groupby('name')[metric].agg(['mean', 'std', 'count']).reset_index()
    background_stats.columns = ['name', 'bg_mean', 'bg_std', 'bg_count']

    # Merge background stats with full dataframe
    df_with_stats = df.merge(background_stats, on='name', how='left')

    # Calculate z-scores
    df_with_stats['z_score'] = (
        (df_with_stats[metric] - df_with_stats['bg_mean']) / df_with_stats['bg_std']
    )

    # Handle edge cases:
    # 1. Taxa not in background (bg_mean is NaN) -> z_score = 100
    df_with_stats.loc[df_with_stats['bg_mean'].isna(), 'z_score'] = 100

    # 2. Taxa in only one background sample (bg_std = 0 or NaN) -> z_score = 100
    df_with_stats.loc[(df_with_stats['bg_std'] == 0) | (df_with_stats['bg_std'].isna()), 'z_score'] = 100

    # 3. Bound z-scores between -100 and 100
    df_with_stats['z_score'] = df_with_stats['z_score'].clip(-100, 100)

    return df_with_stats


def create_plotly_heatmap(df, plot_value='nt_bpm', top_n=10, log=False, all_samples=None):
    """
    Create an interactive Plotly heatmap
    all_samples: list of all sample names to include, even if they have no data
    """

    # convert long df to wide df
    plot_df = df.pivot(index='name', columns='samplename', values=plot_value)
    plot_df.sort_index(level=0, ascending=True, inplace=True)

    # Ensure all samples are included in the plot, even if they have no taxa
    if all_samples is not None:
        for sample in all_samples:
            if sample not in plot_df.columns:
                plot_df[sample] = np.nan  # Add column with NaN values for samples with no data

    # Get top N taxa per sample (excluding NaN values)
    x = plot_df.unstack().groupby(level=0, group_keys=False).nlargest(top_n).to_frame()
    all_top_n_taxa = list(set([i[1] for i in x.index]))  # Convert set to list for pandas indexing

    # filter the plot data to only include taxa in the top_n
    plot_df = plot_df.loc[all_top_n_taxa]

    # Sort columns to ensure consistent order
    plot_df = plot_df.sort_index(axis=1)

    # apply log-scale to value
    if log:
        plot_df = np.log(plot_df + 1)
        value_label = f"log({plot_value} + 1)"
    else:
        value_label = plot_value

    # Replace NaN with 0 for display (will show as white/low value in heatmap)
    plot_df_display = plot_df.fillna(0)

    # Create Plotly heatmap with CZID-like color scheme (yellow to orange to red)
    fig = go.Figure(data=go.Heatmap(
        z=plot_df_display.values,
        x=plot_df_display.columns,
        y=plot_df_display.index,
        colorscale='YlOrRd',
        hoverongaps=False,
        hovertemplate='Sample: %{x}<br>Taxon: %{y}<br>Value: %{z:.2f}<extra></extra>',
        zmin=0,  # Ensure scale starts at 0
        xgap=1,  # Add light grey grid lines between columns
        ygap=1   # Add light grey grid lines between rows
    ))

    # Calculate dimensions to make cells square
    cell_size = 40  # Size of each cell in pixels
    n_rows = len(plot_df)
    n_cols = len(plot_df.columns)

    # Calculate dimensions with padding for labels
    plot_height = n_rows * cell_size + 150  # Add padding for title and x-axis labels
    plot_width = n_cols * cell_size + 200   # Add padding for y-axis labels

    fig.update_layout(
        title=f'CZID Taxon Heatmap - {value_label}',
        xaxis_title='Sample',
        yaxis_title='Taxon',
        height=plot_height,
        width=plot_width,
        xaxis={'side': 'bottom'},
        yaxis={'side': 'left', 'scaleanchor': 'x', 'scaleratio': 1},  # Make cells square
        font=dict(size=10)
    )

    # Update x and y axes
    fig.update_xaxes(tickangle=-45, constrain='domain')
    fig.update_yaxes(tickmode='linear', constrain='domain')

    return fig, plot_df


# Sidebar - Parameter Controls
st.sidebar.header("Heatmap Parameters")

# File uploader
uploaded_files = st.sidebar.file_uploader(
    "Upload CZID Sample Taxon Reports (CSV)",
    type=['csv'],
    accept_multiple_files=True,
    help="Upload multiple CSV files from CZID bulk download",
    key="file_uploader"
)

# Clear files button
if uploaded_files:
    if st.sidebar.button("Clear Files", type="secondary"):
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Filter Settings")

# Metric selection
metric_options = ['nt_bpm', 'nr_bpm', 'nt_base_count', 'nr_base_count',
                  'nt_count', 'nr_count', 'nt_contigs', 'nr_contigs']
metric = st.sidebar.selectbox(
    "Metric to display",
    options=metric_options,
    index=0,  # Default to nt_bpm
    help="Select the metric to visualize in the heatmap"
)

# Tax level selection
tax_level_options = {"Species": 1, "Genus": 2}
tax_level_display = st.sidebar.multiselect(
    "Taxonomic Level",
    options=list(tax_level_options.keys()),
    default=["Species"],
    help="Select the taxonomic level(s) to include"
)
# Convert display names back to numeric values
tax_level = [tax_level_options[level] for level in tax_level_display]

# Category selection
category_list = st.sidebar.multiselect(
    "Categories",
    options=['viruses', 'bacteria', 'archaea', 'eukaryota'],
    default=['viruses'],
    help="Select organism categories to include"
)

st.sidebar.markdown("---")
st.sidebar.subheader("Threshold Filters")

# Threshold filters
min_nt_bpm = st.sidebar.number_input(
    "Min NT bPM",
    min_value=0.0,
    value=10.0,
    step=1.0,
    help="Minimum nucleotide bases per million"
)

min_nr_bpm = st.sidebar.number_input(
    "Min NR bPM",
    min_value=0.0,
    value=0.0,
    step=1.0,
    help="Minimum protein bases per million"
)

min_nt_count = st.sidebar.number_input(
    "Min reads (r)",
    min_value=0,
    value=0,
    step=1,
    help="Minimum nucleotide read count (nt_count)"
)

min_nt_contigs = st.sidebar.number_input(
    "Min NT Contigs",
    min_value=0,
    value=0,
    step=1,
    help="Minimum nucleotide contig bases"
)

min_nr_contigs = st.sidebar.number_input(
    "Min NR Contigs",
    min_value=0,
    value=0,
    step=1,
    help="Minimum protein contig bases"
)

st.sidebar.markdown("---")
st.sidebar.subheader("Display Options")

# Display options
top_n = st.sidebar.slider(
    "Top N taxa per sample",
    min_value=1,
    max_value=50,
    value=5,
    help="Number of top organisms to display per sample"
)

log_transform = st.sidebar.checkbox(
    "Apply log transformation",
    value=True,
    help="Apply log(value + 1) transformation to the data"
)

# Main content area
if uploaded_files:
    st.success(f"✓ {len(uploaded_files)} file(s) uploaded successfully")

    # Show uploaded filenames
    with st.expander("View uploaded files"):
        for file in uploaded_files:
            st.text(f"• {file.name}")

    # Extract sample names from uploaded files
    sample_names = [extract_sample_name(file.name) for file in uploaded_files]

    # Background Model Section
    st.markdown("---")
    st.subheader("Background Model (Optional)")
    st.markdown("Select background samples to calculate z-scores for anomaly detection.")

    col1, col2 = st.columns(2)

    with col1:
        background_samples = st.multiselect(
            "Select Background Samples",
            options=sample_names,
            default=[],
            help="Choose samples to use as background for z-score calculation"
        )

    with col2:
        if background_samples:
            min_z_score = st.number_input(
                "Min Z-score Threshold",
                min_value=-100.0,
                max_value=100.0,
                value=0.0,
                step=0.5,
                help="Only show taxa with z-score above this threshold"
            )
        else:
            min_z_score = None
            st.info("Select background samples to enable z-score filtering")

    # Process button
    st.markdown("---")
    if st.button("Generate Heatmap", type="primary"):
        with st.spinner("Processing CZID reports..."):
            try:
                # Parse all uploaded files
                results_matrix_list = []
                skipped_files = []
                all_sample_names = []  # Track all valid samples, even if they have no data

                for uploaded_file in uploaded_files:
                    df, samplename = read_czid_report(
                        uploaded_file,
                        uploaded_file.name,
                        metric=metric,
                        tax_level=tax_level,
                        category_list=category_list,
                        min_nt_bpm=min_nt_bpm,
                        min_nr_bpm=min_nr_bpm,
                        min_nt_contigs=min_nt_contigs,
                        min_nr_contigs=min_nr_contigs,
                        min_nt_count=min_nt_count
                    )

                    if df is not None:
                        results_matrix_list.append(df)
                        all_sample_names.append(samplename)
                    else:
                        skipped_files.append(uploaded_file.name)

                # Show info about skipped files
                if skipped_files:
                    st.info(f"Note: {len(skipped_files)} file(s) skipped (empty or no data after filtering): {', '.join(skipped_files)}")

                # Check if we have any valid samples
                if not all_sample_names:
                    st.error("No valid data found in any uploaded files. Please check that your files contain data and match the expected CZID format.")
                else:
                    # Concatenate all dataframes (even empty ones)
                    big_df = pd.concat(results_matrix_list, axis=0, ignore_index=True)

                    if big_df.empty:
                        st.warning("No taxa detected with the current filters across all samples. Try adjusting the filter parameters.")
                    else:
                        # Apply background model if selected
                        if background_samples and len(background_samples) > 0:
                            with st.spinner("Calculating z-scores based on background model..."):
                                big_df = calculate_z_scores(big_df, background_samples, metric=metric)

                                # Apply z-score filter BEFORE top N selection
                                if min_z_score is not None:
                                    big_df = big_df[big_df['z_score'] >= min_z_score]

                                    if big_df.empty:
                                        st.warning(f"No taxa detected with z-score >= {min_z_score}. Try lowering the z-score threshold.")
                                        big_df = None  # Signal to skip heatmap generation

                                if big_df is not None and not big_df.empty:
                                    st.success(f"Processed {len(big_df)} records across {len(all_sample_names)} samples (with background model)")
                        else:
                            st.success(f"Processed {len(big_df)} records across {len(all_sample_names)} samples")

                        # Create and display heatmap
                        if big_df is not None and not big_df.empty:
                            with st.spinner("Generating interactive heatmap..."):
                                fig, plot_df = create_plotly_heatmap(
                                    big_df,
                                    plot_value=metric,
                                    top_n=top_n,
                                    log=log_transform,
                                    all_samples=all_sample_names
                                )

                                st.plotly_chart(fig, use_container_width=True)

                                # Download section
                                st.markdown("---")
                                st.subheader("Download Options")

                                col1, col2 = st.columns(2)

                                with col1:
                                    # Download as PNG
                                    st.markdown("**Download as PNG**")
                                    st.info("Click the camera icon in the plotly toolbar above to download as PNG")

                                with col2:
                                    # Download data as CSV
                                    csv_buffer = BytesIO()
                                    plot_df.to_csv(csv_buffer)
                                    csv_buffer.seek(0)

                                    st.download_button(
                                        label="Download Data as CSV",
                                        data=csv_buffer,
                                        file_name="heatmap_data.csv",
                                        mime="text/csv"
                                    )

                                # Display summary statistics
                                with st.expander("View Summary Statistics"):
                                    st.write(f"**Number of taxa displayed:** {len(plot_df)}")
                                    st.write(f"**Number of samples:** {len(plot_df.columns)}")
                                    st.write(f"**Metric:** {metric}")
                                    st.write(f"**Log transformed:** {log_transform}")
                                    if background_samples and len(background_samples) > 0:
                                        st.write(f"**Background samples:** {', '.join(background_samples)}")
                                        st.write(f"**Min z-score:** {min_z_score}")

                                    st.markdown("**Data preview:**")
                                    st.dataframe(plot_df)

            except Exception as e:
                st.error(f"Error processing files: {str(e)}")
                st.exception(e)
else:
    st.info("👈 Upload CZID sample taxon report CSV files using the sidebar to get started")

    # Instructions
    st.markdown("---")
    st.subheader("Instructions")
    st.markdown("""
    ### How to use this app:

    1. **Download your data from CZID:**
       - Use the CZ ID bulk download workflow to download Sample Taxon Reports
       - Navigate to https://czid.org/bulk_downloads
       - Download and unzip the CSV reports

    2. **Upload your files:**
       - Use the file uploader in the sidebar
       - Select multiple CSV files from your CZID download

    3. **Adjust parameters:**
       - Choose the metric to display (default: bases per million - bPM)
       - Set taxonomic level and categories
       - Apply threshold filters to focus on relevant data
       - Adjust display options (top N taxa, log transformation)

    4. **Generate and interact:**
       - Click "Generate Heatmap" to create the visualization
       - Hover over cells to see detailed values
       - Use Plotly controls to zoom, pan, and explore
       - Download the heatmap as PNG or export data as CSV

    ### Default Settings:
    - **Metric:** nt_bpm (nucleotide bases per million)
    - **Taxonomic Level:** Species (1)
    - **Categories:** Viruses
    - **Min NT bPM:** 10
    - **Top N:** 5 taxa per sample
    - **Log Transform:** Enabled
    """)
