import numpy as np
from icecube import dataio, icetray
from skymist.skyscan import SkyScan
import config
cfg = config.config()
import plotting_utilities
import os
import re
import sys
import matplotlib.pyplot as plt
from scipy.stats import norm
import pandas as pd

cfg = config.config()


def extract_run_evtid(filename, pattern):
    """Extract run and evtid from filename using regex."""
    match = re.search(pattern, filename)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None


def process_fits_files(directory, evt_type):
    """Process FITS files and calculate contour areas."""
    if(evt_type=='icecat1'):
        pattern = r"Run(\d+)_(\d+)_"
        file_type="fits.gz"
    if(evt_type=='new'):
        pattern = r"run(\d+)\.evt(\d+)"
        #file_type="_probability.fits.gz"
        file_type='_llh.fits.gz'
    results = []
    for filename in os.listdir(directory):
        if filename.endswith(file_type):
            run, evtid = extract_run_evtid(filename, pattern)
            if run is None:
                print(f"No match found for {filename}.")
                continue
            try:
                area50, area90 = plotting_utilities.calculate_countour_areas_from_fits(directory + filename)
                results.append((run, evtid, area50, area90))
                print(run, evtid, area50, area90)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    return results

def process_pkl_files(path_llh, path_prob, file_type=".pkl"):
    """Process PKL files and calculate contour areas."""
    pattern = r"run(\d+)\.evt(\d+)"
    results = []
    for filename in os.listdir(path_llh):
        if filename.endswith(file_type):
            run, evtid = extract_run_evtid(filename, pattern)
            if run is None:
                print(f"No match found for {filename}.")
                continue
            try:
                area50_llh, area90_llh = plotting_utilities.calculate_contour_areas_from_pkl(path_llh + filename)
                area50_prob, area90_prob = plotting_utilities.calculate_contour_areas_from_pkl(path_prob + filename)
                results.append((run, evtid, area50_llh, area90_llh, area50_prob, area90_prob))
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    return results


def filter_common_ids(data1, data2):
    """Filter rows with common IDs from two datasets."""
    ids1 = set((row[0], row[1]) for row in data1)
    ids2 = set((row[0], row[1]) for row in data2)
    common_ids = ids1.intersection(ids2)
    
    filtered_data1 = [row for row in data1 if (row[0], row[1]) in common_ids]
    filtered_data2 = [row for row in data2 if (row[0], row[1]) in common_ids]
    
    return filtered_data1, filtered_data2


def plot_scatter(x, y, xlabel, ylabel, output_path, color, label=None):
    """Scatter plot with a reference line."""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.tick_params(axis='both', labelsize=14, width=1, length=4)
    plt.setp(ax.spines.values(), linewidth=2)
    plt.scatter(x, y, alpha=0.7, color=color, label=label)
    plt.plot([min(x), max(x)], [min(x), max(x)], 'r--', label="y = x")
    plt.xlabel(xlabel, size=14)
    plt.ylabel(ylabel, size=14)
    plt.legend(fontsize=12)
    plt.grid()
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")


def plot_histogram(data1, data2, labels, colors, xlabel, ylabel, output_path):
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.tick_params(axis='both', labelsize=14, width=1, length=4)
    plt.setp(ax.spines.values(), linewidth=2)

    # Calculate log-transformed data for both datasets
    log_data1 = np.log10(data1)
    log_data2 = np.log10(data2)

    # Determine shared bins for both histograms
    combined_data = np.concatenate([log_data1, log_data2])
    bins = np.histogram_bin_edges(combined_data, bins=50)

    for log_data, label, color in zip([log_data1, log_data2], labels, colors):
        median = np.median(log_data)
        std = np.std(log_data)
        percentiles = np.percentile(log_data, [16, 84])

        # Histogram with shared bins
        counts, bins, patches = plt.hist(
            log_data, bins=bins, align='left', alpha=0.5, lw=2, color=color, label=label
        )
        bin_centers = 0.5 * (bins[:-1] + bins[1:])  # Compute bin centers

        # Compute error bars for the label
        delta_max = 10 ** percentiles[1] - 10 ** median
        delta_min = 10 ** median - 10 ** percentiles[0]
        label = r'Median $\mu \pm \sigma$ = $%.1f^{+%.1f}_{-%.1f}$ deg$^2$' % (10 ** median, delta_max, delta_min)
        plt.axvline(median, color=color, linestyle='--', linewidth=2, label=label)

    plt.xlabel(xlabel, size=14)
    plt.ylabel(ylabel, size=14)
    plt.legend(fontsize=12)
    plt.grid()
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")

# run, evtid, area50, area90
fits_results = process_fits_files('./output/scans/llh_maps/','new')
run_fits = []
evtid_fits = []
area50_llh_fits = []
area90_llh_fits = []
for i in range(len(fits_results)):
    run_fits.append(int(fits_results[i][0]))
    evtid_fits.append(int(fits_results[i][1]))
    area50_llh_fits.append(fits_results[i][2])
    area90_llh_fits.append(fits_results[i][3])
# run, evtid, area50_llh, area90_llh, area50_prob, area90_prob
pkl_results = process_pkl_files('./output/scans/llh_maps/', './output/scans/probability_maps/')
run_pkl = []
evtid_pkl = []
area50_llh_pkl = []
area90_llh_pkl = []
area50_prob_pkl = []
area90_prob_pkl = []
for i in range(len(pkl_results)):
    run_pkl.append(int(pkl_results[i][0]))
    evtid_pkl.append(int(pkl_results[i][1]))
    area50_llh_pkl.append(pkl_results[i][2])
    area90_llh_pkl.append(pkl_results[i][3])
    area50_prob_pkl.append(pkl_results[i][4])
    area90_prob_pkl.append(pkl_results[i][5])

## Filter events of IceCat-1 already reconstructed with IceCat-2
filtered_fits = []
filtered_pkl = []
for i in range(len(fits_results)):
    for j in range(len(pkl_results)):
        if(run_fits[i]==run_pkl[j] and evtid_fits[i]==evtid_pkl[j]):
            filtered_fits.append(fits_results[i])
            filtered_pkl.append(pkl_results[j])

#NumPy arrays for processing
filtered_fits = np.array(filtered_fits)
filtered_pkl = np.array(filtered_pkl)

plot_histogram(filtered_fits[:, 2], filtered_pkl[:, 2],
               ["fits files", "pkl files"], ["blue", "orange"],
               r"log$_{10}$(Area$_{50\%}$/[deg$^2$])", "N",
               'output_plots/comparison_fits_pkl_area50.png')

plot_histogram(filtered_fits[:, 3], filtered_pkl[:, 3],
               ["fits files", "pkl files"], ["blue", "orange"],
               r"log$_{10}$(Area$_{90\%}$/[deg$^2$])", "N",
               'output_plots/comparison_fits_pkl_area90.png')

ratio50 = filtered_fits[:, 2]/filtered_pkl[:, 2]
ratio90 = filtered_fits[:, 3]/filtered_pkl[:, 3]

fig, ax = plt.subplots(figsize=(7, 4))
ax.tick_params(axis='y', labelsize=14, width=1, length=4)
ax.tick_params(axis='x', labelsize=14, width=1, length=4)
ax.tick_params(which='minor', length=2, width=1)
plt.setp(ax.spines.values(), linewidth=2)
plt.hist(np.log10(ratio50), range=(-0.2,0.2), bins=30, alpha=0.7, align='left',label=r'Area50%')
plt.hist(np.log10(ratio90), range=(-0.2,0.2), bins=30,alpha=0.7, align='left',label='Area90%')
plt.axvline(0, lw=3, color='black', linestyle='--')
plt.xlabel(r'log$_{10}$(Area$_{\mathrm{fits file}}$/Area$_{\mathrm{pkl file}}$)', size=14)
plt.yscale('log')
plt.ylabel('N', size=14)
plt.grid()
plt.legend(fontsize=12)
plt.tight_layout()
output_path = 'output_plots/ratio_fits_pkl.png'
plt.savefig(output_path)
print(f"Plot saved to {output_path}")