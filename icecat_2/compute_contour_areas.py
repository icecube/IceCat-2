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
        file_type="_probability.fits.gz"
        #file_type='llh.fits.gz'
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
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    return results

def process_pkl_files(path_llh, path_prob, file_type=".pkl"):
    """Process PKL files and calculate contour areas."""
    pattern = r"run(\d+)\.evt(\d+)"
    results = []
    for filename in os.listdir(path_prob):
        #print(filename)
        if filename.endswith(file_type):
            #print(filename)
            run, evtid = extract_run_evtid(filename, pattern)
            #print(run, evtid)
            if run is None:
                print(f"No match found for {filename}.")
                continue
            try:
                area50_llh, area90_llh = plotting_utilities.calculate_contour_areas_from_pkl(path_llh + filename)
                #area50_llh = 0.0
                #area90_llh = 0.0
                area50_prob, area90_prob = plotting_utilities.calculate_contour_areas_from_pkl(path_prob + filename)
                results.append((run, evtid, area50_llh, area90_llh, area50_prob, area90_prob))
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    return results


def plot_scatter(x, y, x1, y1, xlabel, ylabel, output_path, color, label=None):
    """Scatter plot with a reference line."""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.tick_params(axis='both', labelsize=14, width=1, length=4)
    plt.setp(ax.spines.values(), linewidth=2)
    plt.scatter(x, y, alpha=0.7, color=color, label=label)
    plt.scatter(x1, y1, alpha=0.7, color='darkorange', label='Weird areas in IceCat-1')
    plt.plot([min(x), max(x)], [min(x), max(x)], 'r--', label="y = x")
    plt.xlabel(xlabel, size=14)
    plt.ylabel(ylabel, size=14)
    plt.legend(fontsize=12)
    plt.grid()
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")


def plot_histogram(data1, data2, labels, colors, xlabel, ylabel, output_path, plot_ratio=False):

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.tick_params(axis='both', labelsize=14, width=1, length=4)
    plt.setp(ax.spines.values(), linewidth=2)

    # Calculate log-transformed data for both datasets
    log_data1 = np.log10(data1)
    log_data2 = np.log10(data2)

    # Determine shared bins for both histograms
    combined_data = np.concatenate([log_data1, log_data2])
    #bins = np.histogram_bin_edges(combined_data, bins=50)
    bins = np.linspace(-2.5,3,50)
    
    for log_data, label, color in zip([log_data1, log_data2], labels, colors):
        median = np.median(log_data)
        std = np.std(log_data)
        percentiles = np.percentile(log_data, [15.87, 84.13]) ## 1sigma percentile
        #percentiles = np.percentile(log_data, [2.28, 97.72])   ## 2sigma percentile

        # Histogram with shared bins
        counts, bins, patches = plt.hist(
            log_data, bins=bins, align='left', alpha=0.5, lw=2, color=color, label=label
        )
        #bin_centers = 0.5 * (bins[:-1] + bins[1:])  # Compute bin centers

        # Compute error bars for the label
        delta_max = 10 ** percentiles[1] - 10 ** median
        delta_min = 10 ** median - 10 ** percentiles[0]
        label = r'Median $\mu \pm \sigma$ = $%.1f^{+%.1f}_{-%.1f}$ deg$^2$' % (10 ** median, delta_max, delta_min)
        if(plot_ratio==True): label = r'Median $\mu \pm \sigma$ = $%.1f^{+%.1f}_{-%.1f}$' % (10 ** median, delta_max, delta_min)
        if(plot_ratio==True): plt.axvline(percentiles[0], color=color, linestyle='--', linewidth=2)
        plt.axvline(median, color=color, linestyle='-', linewidth=2, label=label)
        if(plot_ratio==True): plt.axvline(percentiles[1], color=color, linestyle='--', linewidth=2)
        
    plt.xlabel(xlabel, size=14)
    plt.ylabel(ylabel, size=14)
    plt.legend(fontsize=12)
    plt.grid()
    plt.yscale('log')
    if(plot_ratio==False):
        plt.ylim(0,75)
        plt.xlim(-2.5,3)
        plt.legend(fontsize=11,loc='upper right')
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")




# results from IceCat-1 (old processing) saved in fits files (only llh maps)
# run, evtid, area50_llh, area90_llh
fits_results = process_fits_files(cfg.fits_icecat1,'icecat1')
#fits_results = process_fits_files('/data/user/azegarelli/IceCat-2-fits-file-icecat1/docs/IceCat-1-dataverse_files/fits/test/','icecat1')
run_fits = []
evtid_fits = []
area50_llh_fits = []
area90_llh_fits = []
for i in range(len(fits_results)):
    run_fits.append(int(fits_results[i][0]))
    evtid_fits.append(int(fits_results[i][1]))
    area50_llh_fits.append(fits_results[i][2])
    area90_llh_fits.append(fits_results[i][3])

# results for IceCat-2 (new processing) saved pkl files (both llh and probability maps)
# run, evtid, area50_llh, area90_llh, area50_prob, area90_prob
pkl_results = process_pkl_files('./output/scans/llh_maps/', './output/scans/probability_maps/')
#pkl_results = process_pkl_files('./output/scans/test/', './output/scans/test/')
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

print("N. events from IceCat-1 = ", len(fits_results))
print("N. events from IceCat-2 = ", len(pkl_results))

strange_run = [122605,128034,134535,134552]
strange_evt = [60656774,69069846,41069485,68615710]

filtered_fits           = []
filtered_pkl            = []
filtered_fits_strange   = []
filtered_pkl_strange    = []
filtered_fits_nostrange = []
filtered_pkl_nostrange  = []
if(len(fits_results)>len(pkl_results)):
    print("Filter events of IceCat-1 already reconstructed with IceCat-2")
    for i in range(len(fits_results)):
        for j in range(len(pkl_results)):
            if(run_fits[i]==run_pkl[j] and evtid_fits[i]==evtid_pkl[j]):
                filtered_fits.append(fits_results[i])
                filtered_pkl.append(pkl_results[j])
                strange = False
                for k in range(len(strange_run)):
                    if(run_fits[i]==strange_run[k] and evtid_fits[i]==strange_evt[k]): 
                        filtered_fits_strange.append(fits_results[i])
                        filtered_pkl_strange.append(pkl_results[j])
                        strange = True
                if(strange==False):
                    filtered_fits_nostrange.append(fits_results[i])
                    filtered_pks_nostrange.append(pkl_results[j]) 
if(len(fits_results)<len(pkl_results)):
    print("All events of IceCat-1 reconstructed with IceCat-2")
    for j in range(len(pkl_results)):
        for i in range(len(fits_results)):
            if(run_fits[i]==run_pkl[j] and evtid_fits[i]==evtid_pkl[j]):
                filtered_fits.append(fits_results[i])
                filtered_pkl.append(pkl_results[j])
                strange = False
                for k in range(len(strange_run)):
                    if(run_fits[i]==strange_run[k] and evtid_fits[i]==strange_evt[k]): 
                        filtered_fits_strange.append(fits_results[i])
                        filtered_pkl_strange.append(pkl_results[j])
                        strange = True
                if(strange==False):
                    filtered_fits_nostrange.append(fits_results[i])
                    filtered_pkl_nostrange.append(pkl_results[j]) 

#filtered_fits, filtered_pkl = filter_common_ids(fits_results, pkl_results)

#NumPy arrays for processing
filtered_fits = np.array(filtered_fits)
filtered_pkl = np.array(filtered_pkl)

# run, evtid, area50_llh, area90_llh, area50_prob, area90_prob
run_icecat2         = filtered_pkl[:, 0]
evtid_icecat2       = filtered_pkl[:, 1]
area50_llh_icecat2  = filtered_pkl[:, 2]
area50_prob_icecat2 = filtered_pkl[:, 4]
area90_llh_icecat2  = filtered_pkl[:, 3]
area90_prob_icecat2 = filtered_pkl[:, 5]

run_icecat1         = filtered_fits[:, 0]
evtid_icecat1       = filtered_fits[:, 1]
area50_icecat1      = filtered_fits[:, 2]
area90_icecat1      = filtered_fits[:, 3]

#NumPy arrays for processing
filtered_fits_strange = np.array(filtered_fits_strange)
filtered_pkl_strange = np.array(filtered_pkl_strange)

# run, evtid, area50_llh, area90_llh, area50_prob, area90_prob
run_icecat2_strange         = filtered_pkl_strange[:, 0]
evtid_icecat2_strange       = filtered_pkl_strange[:, 1]
area50_llh_icecat2_strange  = filtered_pkl_strange[:, 2]
area50_prob_icecat2_strange = filtered_pkl_strange[:, 4]
area90_llh_icecat2_strange  = filtered_pkl_strange[:, 3]
area90_prob_icecat2_strange = filtered_pkl_strange[:, 5]

run_icecat1_strange         = filtered_fits_strange[:, 0]
evtid_icecat1_strange       = filtered_fits_strange[:, 1]
area50_icecat1_strange      = filtered_fits_strange[:, 2]
area90_icecat1_strange      = filtered_fits_strange[:, 3]

#NumPy arrays for processing
filtered_fits_nostrange = np.array(filtered_fits_nostrange)
filtered_pkl_nostrange = np.array(filtered_pkl_nostrange)

# run, evtid, area50_llh, area90_llh, area50_prob, area90_prob
run_icecat2_nostrange         = filtered_pkl_nostrange[:, 0]
evtid_icecat2_nostrange       = filtered_pkl_nostrange[:, 1]
area50_llh_icecat2_nostrange  = filtered_pkl_nostrange[:, 2]
area50_prob_icecat2_nostrange = filtered_pkl_nostrange[:, 4]
area90_llh_icecat2_nostrange  = filtered_pkl_nostrange[:, 3]
area90_prob_icecat2_nostrange = filtered_pkl_nostrange[:, 5]

run_icecat1_nostrange         = filtered_fits_nostrange[:, 0]
evtid_icecat1_nostrange       = filtered_fits_nostrange[:, 1]
area50_icecat1_nostrange      = filtered_fits_nostrange[:, 2]
area90_icecat1_nostrange      = filtered_fits_nostrange[:, 3]

'''
check_file_old = cfg.alerts_table_dir+"division_LED_HED_old_events.csv"
check_file_new = cfg.alerts_table_dir+"division_LED_HED_i3live_events.csv"
run_old, evt_old = np.loadtxt(check_file_old, usecols=(0,1), unpack=True, dtype=int, delimiter=',')
run_new, evt_new = np.loadtxt(check_file_new, usecols=(0,1), unpack=True, dtype=int, delimiter=',')
evt_type_old     = np.loadtxt(check_file_old, usecols=(3), unpack=True, dtype=str, delimiter=',')
evt_type_new     = np.loadtxt(check_file_new, usecols=(3), unpack=True, dtype=str, delimiter=',')

indices_to_remove = []
for i in range(len(run_icecat1)):
    for j in range(len(run_old)):
        if(run_icecat1[i]==run_old[j] and evtid_icecat1[i]==evt_old[j]):
            if(evt_type_old[j]=='LED'): indices_to_remove.append(i)
    for j in range(len(run_new)):
        if(run_icecat1[i]==run_new[j] and evtid_icecat1[i]==evt_new[j]):
            if(evt_type_new[j]=='LED'): indices_to_remove.append(i)

run_icecat1 = np.delete(run_icecat1, indices_to_remove, axis=0)
evtid_icecat1 = np.delete(evtid_icecat1, indices_to_remove, axis=0)
area50_icecat1 = np.delete(area50_icecat1, indices_to_remove, axis=0)
area90_icecat1 = np.delete(area90_icecat1, indices_to_remove, axis=0)

run_icecat2 = np.delete(run_icecat2, indices_to_remove, axis=0)
evtid_icecat2 = np.delete(evtid_icecat2, indices_to_remove, axis=0)
area50_llh_icecat2 = np.delete(area50_llh_icecat2, indices_to_remove, axis=0)
area50_prob_icecat2 = np.delete(area50_prob_icecat2, indices_to_remove, axis=0)
area90_llh_icecat2 = np.delete(area90_llh_icecat2, indices_to_remove, axis=0)
area90_prob_icecat2 = np.delete(area90_prob_icecat2, indices_to_remove, axis=0)
'''

check_file_old = cfg.alerts_table_dir+"division_LED_HED_old_events.csv"
check_file_new = cfg.alerts_table_dir+"division_LED_HED_i3live_events.csv"
run_old, evt_old = np.loadtxt(check_file_old, usecols=(0,1), unpack=True, dtype=int, delimiter=',')
run_new, evt_new = np.loadtxt(check_file_new, usecols=(0,1), unpack=True, dtype=int, delimiter=',')
evt_type_old     = np.loadtxt(check_file_old, usecols=(3), unpack=True, dtype=str, delimiter=',')
evt_type_new     = np.loadtxt(check_file_new, usecols=(3), unpack=True, dtype=str, delimiter=',')

count_hed = 0
count_led = 0
for i in range(len(run_icecat1)):
    for j in range(len(run_old)):
        if(run_icecat1[i]==run_old[j] and evtid_icecat1[i]==evt_old[j]):
            if(evt_type_old[j]=='HED'): count_hed+=1
            if(evt_type_old[j]=='LED'): count_led+=1
    for j in range(len(run_new)):
        if(run_icecat1[i]==run_new[j] and evtid_icecat1[i]==evt_new[j]):
            if(evt_type_new[j]=='HED'): count_hed+=1
            if(evt_type_new[j]=='LED'): count_led+=1

print('Number of IceCat-1 events reconstructed with new reco = ', count_led+count_hed)
print('                                                  HED = ', count_hed)
print('                                                  LED = ', count_led)

print(len(area90_icecat1), len(area90_prob_icecat2))
plot_scatter(area50_icecat1_nostrange, area50_prob_icecat2_nostrange,area50_icecat1_strange, area50_prob_icecat2_strange,
             r"Area$_{50\%}$ (IceCat1) [deg$^2$]", r"Area$_{50\%}$ (IceCat2) [deg$^2$]",
             'output_plots/areas50_comparison_llh_prob.png', 'blue')

plot_scatter(area90_icecat1_nostrange, area90_prob_icecat2_nostrange,area90_icecat1_strange, area90_prob_icecat2_strange,
             r"Area$_{90\%}$ (IceCat1) [deg$^2$]", r"Area$_{90\%}$ (IceCat2) [deg$^2$]",
             'output_plots/areas90_comparison_llh_prob.png', 'green')
plot_scatter(np.log10(area50_icecat1_nostrange), np.log10(area50_prob_icecat2_nostrange),np.log10(area50_icecat1_strange), np.log10(area50_prob_icecat2_strange),
             r"log$_{10}$(Area$_{50\%}$/[deg$^2$]) (IceCat-1)", r"log$_{10}$(Area$_{50\%}$/[deg$^2$]) (IceCat-2)",
             'output_plots/logareas50_comparison_llh_prob.png', 'blue')

plot_scatter(np.log10(area90_icecat1_nostrange), np.log10(area90_prob_icecat2_nostrange),np.log10(area90_icecat1_strange), np.log10(area90_prob_icecat2_strange),
             r"log$_{10}$(Area$_{90\%}$/[deg$^2$]) (IceCat-1)", r"log$_{10}$(Area$_{90\%}$/[deg$^2$]) (IceCat-2)",
             'output_plots/logareas90_comparison_llh_prob.png', 'green')

plot_scatter(area50_icecat1_nostrange, area50_llh_icecat2_nostrange,area50_icecat1_strange, area50_llh_icecat2_strange,
             r"Area$_{50\%}$ (IceCat1) [deg$^2$] ", r"Area$_{50\%}$ (IceCat2) [deg$^2$]",
             'output_plots/areas50_comparison_llh_llh.png', 'blue')

plot_scatter(area90_icecat1_nostrange, area90_llh_icecat2_nostrange,area90_icecat1_strange, area90_llh_icecat2_strange,
             r"Area$_{90\%}$ (IceCat1)", r"Area$_{90\%}$ (IceCat2)",
             'output_plots/areas90_comparison_llh_llh.png', 'green')

plot_scatter(np.log10(area50_icecat1_nostrange), np.log10(area50_llh_icecat2_nostrange),area90_icecat1_strange, area90_llh_icecat2_strange,
             r"log$_{10}$(Area$_{50\%}$/[deg$^2$]) (IceCat-1)", r"log$_{10}$(Area$_{50\%}$/[deg$^2$]) (IceCat-2)",
             'output_plots/logareas50_comparison_llh_llh.png', 'blue')

plot_scatter(np.log10(area90_icecat1_nostrange), np.log10(area90_llh_icecat2_nostrange),np.log10(area90_icecat1_strange), np.log10(area90_llh_icecat2_strange),
             r"log$_{10}$(Area$_{90\%}$/[deg$^2$]) (IceCat-1)", r"log$_{10}$(Area$_{90\%}$/[deg$^2$]) (IceCat-2)",
             'output_plots/logareas90_comparison_llh_llh.png', 'green')


################

plot_histogram(area50_icecat1, area50_llh_icecat2,
               ["IceCat1", "IceCat2"], ["blue", "orange"],
               r"log$_{10}$(Area$_{50\%}$/[deg$^2$])", "N",
               'output_plots/areas50_comparison_histogram_llh_llh.png')

plot_histogram(area50_icecat1, area50_prob_icecat2,
               ["IceCat1", "IceCat2"], ["blue", "orange"],
               r"log$_{10}$(Area$_{50\%}$/[deg$^2$])", "N",
               'output_plots/areas50_comparison_histogram_llh_prob.png')

plot_histogram(area90_icecat1, area90_llh_icecat2,
               ["IceCat1", "IceCat2"], ["blue", "orange"],
               r"log$_{10}$(Area$_{90\%}$/[deg$^2$])", "N",
               'output_plots/areas90_comparison_histogram_llh_llh.png')

plot_histogram(area90_icecat1, area90_prob_icecat2,
               ["IceCat1", "IceCat2"], ["blue", "orange"],
               r"log$_{10}$(Area$_{90\%}$/[deg$^2$])", "N",
               'output_plots/areas90_comparison_histogram_llh_prob.png')

##################

plot_histogram(area50_icecat1_nostrange, area50_llh_icecat2,
               ["IceCat1", "IceCat2"], ["blue", "orange"],
               r"log$_{10}$(Area$_{50\%}$/[deg$^2$])", "N",
               'output_plots/areas50_comparison_histogram_llh_llh_nostrange.png')

plot_histogram(area50_icecat1_nostrange, area50_prob_icecat2,
               ["IceCat1", "IceCat2"], ["blue", "orange"],
               r"log$_{10}$(Area$_{50\%}$/[deg$^2$])", "N",
               'output_plots/areas50_comparison_histogram_llh_prob_nostrange.png')

plot_histogram(area90_icecat1_nostrange, area90_llh_icecat2,
               ["IceCat1", "IceCat2"], ["blue", "orange"],
               r"log$_{10}$(Area$_{90\%}$/[deg$^2$])", "N",
               'output_plots/areas90_comparison_histogram_llh_llh_nostrange.png')

plot_histogram(area90_icecat1_nostrange, area90_prob_icecat2,
               ["IceCat1", "IceCat2"], ["blue", "orange"],
               r"log$_{10}$(Area$_{90\%}$/[deg$^2$])", "N",
               'output_plots/areas90_comparison_histogram_llh_prob_nostrange.png')

##################

ratio_area50 = area50_icecat1/area50_prob_icecat2
ratio_area90 = area90_icecat1/area90_prob_icecat2
        
count=0
print('Run\t EvtID \t Area90_IceCat1 \t Area90_IceCat2 \t Ratio_Area90_IceCat2-IceCat1')
for i in range(len(ratio_area90)):
    if(area90_prob_icecat2[i]>5*area90_icecat1[i]):
        print(int(run_icecat1[i]),int(evtid_icecat1[i]),area90_icecat1[i],area90_prob_icecat2[i],area90_prob_icecat2[i]/area90_icecat1[i])
        count+=1
print('N events where IceCat2 area is higher than IceCat1 = ', count)

'''
count=0
print('Run\t EvtID \t Area90_IceCat1 \t Area90_IceCat2 \t Ratio_Area90_IceCat1-IceCat2')
for i in range(len(ratio_area90)):
    if(np.log10(area90_icecat1[i])<-0.3):
        print(int(run_icecat1[i]),int(evtid_icecat1[i]),area90_icecat1[i],area90_prob_icecat2[i],area90_icecat1[i]/area90_prob_icecat2[i])
        count+=1
'''

plot_histogram(ratio_area50, ratio_area90,
               ["Area$_{50\%}$", "Area$_{90\%}$"], ["blue", "orange"],
               r"log$_{10}$(Area$_{\mathrm{IceCat-1}}$/Area$_{\mathrm{IceCat-2}}$)", "N",
               'output_plots/ratio_prob.png',plot_ratio=True)

ratio_area50 = area50_icecat1/area50_llh_icecat2
ratio_area90 = area90_icecat1/area90_llh_icecat2

plot_histogram(ratio_area50, ratio_area90,
               ["Area$_{50\%}$", "Area$_{90\%}$"], ["blue", "orange"],
               r"log$_{10}$(Area$_{\mathrm{IceCat-1}}$/Area$_{\mathrm{IceCat-2}}$)", "N",
               'output_plots/ratio_llh.png',plot_ratio=True)

#####

ratio_area50_strange = area50_icecat1_strange/area50_prob_icecat2_strange
ratio_area90_strange = area90_icecat1_strange/area90_prob_icecat2_strange

plot_histogram(ratio_area50_strange, ratio_area90_strange,
               ["Area$_{50\%}$", "Area$_{90\%}$"], ["blue", "orange"],
               r"log$_{10}$(Area$_{\mathrm{IceCat-1}}$/Area$_{\mathrm{IceCat-2}}$)", "N",
               'output_plots/ratio_prob_strange.png',plot_ratio=True)

ratio_area50_strange = area50_icecat1_strange/area50_llh_icecat2_strange
ratio_area90_strange = area90_icecat1_strange/area90_llh_icecat2_strange

plot_histogram(ratio_area50_strange, ratio_area90_strange,
               ["Area$_{50\%}$", "Area$_{90\%}$"], ["blue", "orange"],
               r"log$_{10}$(Area$_{\mathrm{IceCat-1}}$/Area$_{\mathrm{IceCat-2}}$)", "N",
               'output_plots/ratio_llh_strange.png',plot_ratio=True)

####

ratio_area50_nostrange = area50_icecat1_nostrange/area50_prob_icecat2_nostrange
ratio_area90_nostrange = area90_icecat1_nostrange/area90_prob_icecat2_nostrange

plot_histogram(ratio_area50_nostrange, ratio_area90_nostrange,
               ["Area$_{50\%}$", "Area$_{90\%}$"], ["blue", "orange"],
               r"log$_{10}$(Area$_{\mathrm{IceCat-1}}$/Area$_{\mathrm{IceCat-2}}$)", "N",
               'output_plots/ratio_prob_nostrange.png',plot_ratio=True)

ratio_area50_nostrange = area50_icecat1_nostrange/area50_llh_icecat2_nostrange
ratio_area90_nostrange = area90_icecat1_nostrange/area90_llh_icecat2_nostrange

plot_histogram(ratio_area50_nostrange, ratio_area90_nostrange,
               ["Area$_{50\%}$", "Area$_{90\%}$"], ["blue", "orange"],
               r"log$_{10}$(Area$_{\mathrm{IceCat-1}}$/Area$_{\mathrm{IceCat-2}}$)", "N",
               'output_plots/ratio_llh_nostrange.png',plot_ratio=True)