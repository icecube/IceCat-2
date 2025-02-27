import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import config
cfg = config.config()

def angular_distance(lon1, lat1, lon2, lat2):
    c1 = np.cos(lat1)
    c2 = np.cos(lat2)
    s1 = np.sin(lat1)
    s2 = np.sin(lat2)
    sd = np.sin(lon2 - lon1)
    cd = np.cos(lon2 - lon1)

    return np.arctan2(
        np.hypot(c2 * sd, c1 * s2 - s1 * c2 * cd),
        s1 * s2 + c1 * c2 * cd
    )

file_path_icecat1 = cfg.alerts_table_dir + 'IceCat-1-dataverse_files/IceCube_Gold_Bronze_Tracks.csv'
data_icecat1 = pd.read_csv(file_path_icecat1)

file_path_new_reco = cfg.alerts_table_dir + 'output_reco.csv'
new_reco = pd.read_csv(file_path_new_reco)

# Ensure RA and Dec columns are correctly named and in degrees
run_icecat1 = data_icecat1['RUNID']
evt_icecat1 = data_icecat1['EVENTID']
run_new = new_reco['Run']
evt_new = new_reco['EventID']
ra_icecat1 = data_icecat1['RA']
dec_icecat1 = data_icecat1['DEC']
ra_new = new_reco['RA_90']
dec_new = new_reco['Dec_90']

# Step 1: Merge the DataFrames on 'RUNID' and 'EVENTID' (or 'Run' and 'EventID' in the new_reco DataFrame)
#common_events = pd.merge(data_icecat1, new_reco, left_on=['RUNID', 'EVENTID'], right_on=['Run', 'EventID'], how='inner')
common_events = new_reco.merge(data_icecat1, left_on=['Run', 'EventID'], right_on=['RUNID', 'EVENTID'], how='inner')

#print(common_events['RA'])
#print(common_events['RA_90'])

# Step 2: Extract the relevant columns from the merged DataFrame
ra_icecat1 = common_events['RA']
dec_icecat1 = common_events['DEC']
ra_new = common_events['RA_90']
dec_new = common_events['Dec_90']
run_icecat1 = common_events['RUNID']
evtid_icecat1 = common_events['EVENTID']
run_new = common_events['Run']
evtid_new = common_events['EventID']

ang_dist = np.zeros(shape=len(ra_icecat1), dtype=float)
for i in range(len(ra_icecat1)):
    ang_dist[i]=angular_distance(np.radians(ra_icecat1[i]),np.radians(dec_icecat1[i]),np.radians(ra_new[i]),np.radians(dec_new[i]))
    print(i,run_icecat1[i],int(run_new[i]),' --- ',evtid_icecat1[i],int(evtid_new[i]),'--->',np.degrees(ang_dist[i]))

fig, ax = plt.subplots(figsize=(7,4))
ax.tick_params(axis='y', labelsize=14, width=1, length=4)
ax.tick_params(axis='x', labelsize=14, width=1, length=4)
ax.tick_params(which='minor', length=2, width=1)
plt.setp(ax.spines.values(), linewidth=2)
plt.hist(ra_icecat1,align='left',bins=100,range=(0,360),label=r'IceCat-1',histtype='step',lw=2)
plt.hist(ra_new,align='left',bins=100,range=(0,360),label=r'New realtime alerts',lw=2,histtype='step')
plt.xlabel(r'RA [deg]',size=14)
plt.ylabel(r'N',size=14)
plt.legend(fontsize=12)
#plt.yscale('log')
plt.grid()
plt.tight_layout()
output_path = 'output_plots/reco_comparison_RA.png'
plt.savefig(output_path)

fig, ax = plt.subplots(figsize=(7,4))
ax.tick_params(axis='y', labelsize=14, width=1, length=4)
ax.tick_params(axis='x', labelsize=14, width=1, length=4)
ax.tick_params(which='minor', length=2, width=1)
plt.setp(ax.spines.values(), linewidth=2)
plt.hist(dec_icecat1,align='left',bins=100,range=(-100,100),label=r'IceCat-1',histtype='step',lw=2)
plt.hist(dec_new,align='left',bins=100,range=(-100,100),label=r'New realtime alerts',lw=2,histtype='step')
plt.xlabel(r'Dec [deg]',size=14)
plt.ylabel(r'N',size=14)
plt.legend(fontsize=12)
#plt.yscale('log')
plt.grid()
plt.tight_layout()
output_path = 'output_plots/reco_comparison_Dec.png'
plt.savefig(output_path)

ang_dist = angular_distance(np.radians(ra_icecat1),np.radians(dec_icecat1),np.radians(ra_new),np.radians(dec_new))

for i in range(len(ang_dist)):
    if(np.degrees(ang_dist[i])>10):
        print(common_events['Run'][i],common_events['EventID'][i])
        print(common_events['RA'][i],common_events['DEC'][i],common_events['RA_90'][i],common_events['Dec_90'][i])
        print(ang_dist[i])
        
events_above_threshold = ang_dist[ang_dist > np.radians(30)]
print(events_above_threshold)
high_indices = np.where(ang_dist > np.radians(30))[0]  # Extract indices where ang_dist is 0
print(high_indices)
for i in range(len(ra_icecat1)):
    print(i, run_icecat1[i], evt_icecat1[i])

for idx in high_indices:
    ra = ra_icecat1.iloc[idx]
    dec = dec_icecat1.iloc[idx]
    run = run_icecat1.iloc[idx]
    evt = evt_icecat1.iloc[idx]
    print("\n")
    print(f"Run: {run_new.iloc[idx]}, EventID: {evtid_new.iloc[idx]}, AngDist [deg]: {np.degrees(ang_dist.iloc[idx])}")
    print(f"RA old: {ra_icecat1.iloc[idx]}, RA new: {ra_new.iloc[idx]}, Dec old: {dec_icecat1.iloc[idx]}, Dec new: {dec_new.iloc[idx]}")


null_indices = np.where(ang_dist == 0)[0]  # Extract indices where ang_dist is 0
# Print the corresponding RA, Dec, Run, and EventID values
print("RA, Dec, Run, and EventID corresponding to null angular distances:")
for idx in null_indices:
    ra = ra_icecat1.iloc[idx]
    dec = dec_icecat1.iloc[idx]
    run = run_icecat1.iloc[idx]
    evt = evt_icecat1.iloc[idx]
    print(f"RA: {ra}, Dec: {dec}, Run: {run}, EventID: {evt}")

# Remove elements with 0 from ang_dist
ang_dist_filtered = ang_dist[ang_dist != 0]

median = np.median(np.degrees(ang_dist))
percentiles = np.percentile(np.degrees(ang_dist), [16, 84])
delta_max = percentiles[1] - median
delta_min = median - percentiles[0]
label = r'Median $\mu \pm \sigma$ = $%.2f^{+%.2f}_{-%.2f}$ deg' %(median, delta_max, delta_min)
#print(len(ang_dist_filtered))

fig, ax = plt.subplots(figsize=(7,4))
ax.tick_params(axis='y', labelsize=14, width=1, length=4)
ax.tick_params(axis='x', labelsize=14, width=1, length=4)
ax.tick_params(which='minor', length=2, width=1)
plt.setp(ax.spines.values(), linewidth=2)
plt.hist(np.log10(np.degrees(ang_dist_filtered)),align='left',histtype='step',lw=2,bins=50)
plt.xlabel(r'log$_{10}$(|dir$_{\mathrm{BestFit},\mathrm{IceCat1}}$-dir$_{\mathrm{BestFit},\mathrm{new}}$|/[deg])',size=14)
plt.axvline(np.log10(median), color='red', linestyle='--', linewidth=2, label=label)
plt.ylabel(r'N',size=14)
#plt.yscale('log')
plt.legend(fontsize=12,loc='upper right')
plt.grid()
plt.tight_layout()
output_path = 'output_plots/angular_distances_logscale.png'
plt.savefig(output_path,dpi=300)

fig, ax = plt.subplots(figsize=(7,4))
ax.tick_params(axis='y', labelsize=14, width=1, length=4)
ax.tick_params(axis='x', labelsize=14, width=1, length=4)
ax.tick_params(which='minor', length=2, width=1)
plt.setp(ax.spines.values(), linewidth=2)
plt.hist(np.degrees(ang_dist),align='left',histtype='step',lw=2,bins=60)
plt.xlabel(r'|dir$_{best fit,\mathrm{IceCat1}}$-dir$_{best fit,\mathrm{new}}$| [deg]',size=14)
plt.axvline(median, color='red', linestyle='--', linewidth=2, label=label)
plt.ylabel(r'N',size=14)
plt.yscale('log')
plt.grid()
plt.legend(fontsize=12)
plt.tight_layout()
output_path = 'output_plots/angular_distances.png'
plt.savefig(output_path,dpi=300)

ra90_min_icecat1 = data_icecat1['RA_ERR_MINUS']
ra90_max_icecat1 = data_icecat1['RA_ERR_PLUS']
dec90_min_icecat1 = data_icecat1['DEC_ERR_MINUS']
dec90_max_icecat1 = data_icecat1['DEC_ERR_PLUS']

ra90_min_new = new_reco['RA_90_min']
ra90_max_new = new_reco['RA_90_max']
dec90_min_new = new_reco['Dec_90_min']
dec90_max_new = new_reco['Dec_90_max']

areas_icecat1 = np.abs(ra90_max_icecat1 - ra90_min_icecat1) * np.abs(dec90_max_icecat1 - dec90_min_icecat1)
areas_new = np.abs(ra90_max_new - ra90_min_new) * np.abs(dec90_max_new - dec90_min_new)

print(len(areas_icecat1))
print(len(areas_new))

print(areas_icecat1.min(),areas_icecat1.max())
print(areas_new.min(),areas_new.max())

fig, ax = plt.subplots(figsize=(7,4))
bins = np.logspace(0, np.log10(100), 30)
plt.hist(areas_icecat1, label="IceCat1 Areas",bins=bins)
plt.hist(areas_new, label="New Reconstruction Areas",bins=bins)
plt.xlabel("N")
plt.ylabel("Rectangular Area (deg²)")
plt.title("Comparison of Rectangular Areas (90% Confidence Regions)")
plt.legend(fontsize=12)
plt.xscale('log')
plt.grid()
plt.tight_layout()
output_path = 'output_plots/areas90%.png'
plt.savefig(output_path)

common_events = pd.merge(
    data_icecat1,
    new_reco,
    left_on=["RUNID", "EVENTID"],  # Columns in data_icecat1
    right_on=["Run", "EventID"]   # Columns in new_reco
)

print(len(common_events))
print(common_events.columns)

ra90_min_icecat1 = common_events['RA_ERR_MINUS']
ra90_max_icecat1 = common_events['RA_ERR_PLUS']
dec90_min_icecat1 = common_events['DEC_ERR_MINUS']
dec90_max_icecat1 = common_events['DEC_ERR_PLUS']

ra90_min_new = common_events['RA_90_min']
ra90_max_new = common_events['RA_90_max']
dec90_min_new = common_events['Dec_90_min']
dec90_max_new = common_events['Dec_90_max']

areas_icecat1 = np.abs(ra90_max_icecat1 - ra90_min_icecat1) * np.abs(dec90_max_icecat1 - dec90_min_icecat1)
areas_new = np.abs(ra90_max_new - ra90_min_new) * np.abs(dec90_max_new - dec90_min_new)

ratio_areas = areas_icecat1/areas_new
print(ratio_areas)
# Check for infinity values in the ratio_areas Series
inf_mask = np.isinf(ratio_areas)

# Get the count of inf values
inf_count = inf_mask.sum()
print("Number of inf values in the ratio_areas:")
print(inf_count)
# Remove the rows where the ratio is inf
ratio_areas_cleaned = ratio_areas[~inf_mask]
# Check the shape after cleaning
print(f"Shape after removing rows with inf values: {ratio_areas_cleaned.shape}")

#ratio_areas_cleaned = ratio_areas_cleaned[ratio_areas_cleaned<1000]

fig, ax = plt.subplots(figsize=(7,4))
plt.hist(ratio_areas_cleaned, bins=50)
plt.xlabel("N")
plt.ylabel("Area$_{90\%\,\mathrm{IceCat1}}$/Area$_{90\%\,\mathrm{new}}$")
plt.grid()
plt.yscale('log')
plt.tight_layout()
output_path = 'output_plots/diff_areas90%.png'
plt.savefig(output_path)
 