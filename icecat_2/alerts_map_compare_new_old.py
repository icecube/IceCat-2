import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.coordinates import SkyCoord
from astropy.visualization import astropy_mpl_style
import config
cfg = config.config()
from astropy import units as u
import plotting_utilities

#plt.style.use(astropy_mpl_style)  # Optional for better styling

# Ensure that the paths are correct
file_path_icecat1 = cfg.alerts_table_dir + 'IceCat-1-dataverse_files/IceCube_Gold_Bronze_Tracks.csv'
data_icecat1 = pd.read_csv(file_path_icecat1)
file_path_new_reco = cfg.alerts_table_dir + 'output_reco.csv'
#file_path_new_reco = cfg.alerts_table_dir + 'output_reco_noveto.csv'
new_reco = pd.read_csv(file_path_new_reco)

# Ensure RA and Dec columns are correctly named and in degrees
run_icecat1 = data_icecat1['RUNID']
evt_icecat1 = data_icecat1['EVENTID']
cr_veto = data_icecat1['CR_VETO']
run_new = new_reco['Run']
evt_new = new_reco['EventID']
ra_icecat1 = data_icecat1['RA']  # Replace with the column name for Right Ascension
dec_icecat1 = data_icecat1['DEC']  # Replace with the column name for Declination
ra_new = new_reco['RA_90']  # Replace with the column name for Right Ascension
dec_new = new_reco['Dec_90']  # Replace with the column name for Declination

'''
vetoed = []
for i in range(len(cr_veto)):
    if(cr_veto[i]==True): vetoed.append(i)
print(vetoed)
#data_icecat1 = data_icecat1.drop(index=vetoed).reset_index(drop=True)
for i in range(len(run_icecat1)):
    for j in range(len(vetoed)):
        if(i==vetoed[j]):
            print(run_icecat1[i],evt_icecat1[i])

print(f"Events removed because of IceTop veto: {len(vetoed)}")
data_icecat1 = data_icecat1.drop(index=vetoed).reset_index(drop=True)
run_icecat1 = data_icecat1['RUNID']
evt_icecat1 = data_icecat1['EVENTID']
ra_icecat1 = data_icecat1['RA']
dec_icecat1 = data_icecat1['DEC'] 
'''

# Step 1: Merge the DataFrames on 'RUNID' and 'EVENTID' (or 'Run' and 'EventID' in the new_reco DataFrame)
common_events = pd.merge(data_icecat1, new_reco, left_on=['RUNID', 'EVENTID'], right_on=['Run', 'EventID'], how='inner')

# Step 2: Extract the relevant columns from the merged DataFrame
ra_icecat1_selected = common_events['RA']
dec_icecat1_selected = common_events['DEC']
ra_new_selected = common_events['RA_90']
dec_new_selected = common_events['Dec_90']

# Step 3: Output or further process the selected events
print(common_events[['RUNID', 'EVENTID', 'RA', 'DEC', 'RA_90', 'Dec_90']])

'''
run1, evt1 = np.loadtxt(cfg.alerts_table_dir+'scans_completed_old_evts.txt',usecols=(0,1),unpack=True,dtype=int)
run2, evt2 = np.loadtxt(cfg.alerts_table_dir+'scans_completed_i3live_evts.txt',usecols=(0,1),unpack=True,dtype=int)
algo1 = np.loadtxt(cfg.alerts_table_dir+'scans_completed_old_evts.txt',usecols=(2),unpack=True,dtype=str)
algo2 = np.loadtxt(cfg.alerts_table_dir+'scans_completed_i3live_evts.txt',usecols=(2),unpack=True,dtype=str)
run = np.concatenate((run1, run2))
evt = np.concatenate((evt1, evt2))
algo = np.concatenate((algo1, algo2))

ang_dist_rad = plotting_utilities.angular_distance(np.radians(ra_icecat1),np.radians(dec_icecat1),np.radians(ra_new),np.radians(dec_new))
ang_dist = np.degrees(ang_dist_rad)
#ang_dist=ang_dist[ang_dist<1]
mask = ang_dist > 140
filtered_events = data_icecat1[mask][['RUNID', 'EVENTID']]
print(filtered_events)

# Converti i valori filtrati in array numpy per confronto
filtered_run = filtered_events['RUNID'].values
filtered_evt = filtered_events['EVENTID'].values
# Verifica corrispondenze
matched_algos = []
splinempe=0
millipede_wilks=0
for frun, fevt in zip(filtered_run, filtered_evt):
    matches = (run == frun) & (evt == fevt)  # Trova corrispondenze
    if np.any(matches):  # Se c'è almeno una corrispondenza
        matched_algos.extend(algo[matches])  # Aggiungi gli `algo` corrispondenti
        if(algo[matches]=='splinempe'): splinempe+=1
        if(algo[matches]=='millipede_wilks'): millipede_wilks+=1


print(splinempe,millipede_wilks,len(matched_algos))
quit()

fig, ax = plt.subplots(figsize=(7, 4))
ax.tick_params(axis='y', labelsize=14, width=1, length=4)
ax.tick_params(axis='x', labelsize=14, width=1, length=4)
ax.tick_params(which='minor', length=2, width=1)
plt.setp(ax.spines.values(), linewidth=2)
plt.hist(ang_dist,align='left')
plt.xlabel(r'|dir$_{90\%\,\mathrm{IceCat1}}$-dir$_{90\%\,\mathrm{new}}$| [deg]',size=14)
plt.ylabel(r'N',size=14)
#plt.xscale('log')
#plt.yscale('log')
plt.grid()
plt.tight_layout()
output_path = 'output_plots/angular_distances.png'
plt.savefig(output_path)
'''

ra_diff_raw = ra_icecat1_selected-ra_new_selected
# Adjust RA difference for the circular nature (RA ranges from 0 to 360 degrees)
ra_diff = (ra_diff_raw + 180) % 360 - 180
fig, ax = plt.subplots(figsize=(7, 4))
ax.tick_params(axis='y', labelsize=14, width=1, length=4)
ax.tick_params(axis='x', labelsize=14, width=1, length=4)
ax.tick_params(which='minor', length=2, width=1)
plt.setp(ax.spines.values(), linewidth=2)
plt.hist(np.abs(ra_diff_raw),align='left',bins=50)
plt.xlabel(r'|RA$_{\mathrm{IceCat1}}$-RA$_{\mathrm{new}}$| [deg]',size=14)
plt.ylabel(r'N',size=14)
#plt.xscale('log')
plt.yscale('log')
plt.grid()
plt.tight_layout()
output_path = 'output_plots/RA_comparison.png'
plt.savefig(output_path)

# Calculate the difference in Dec (no need to adjust Dec because it ranges from -90 to +90 degrees)
fig, ax = plt.subplots(figsize=(7, 4))
ax.tick_params(axis='y', labelsize=14, width=1, length=4)
ax.tick_params(axis='x', labelsize=14, width=1, length=4)
ax.tick_params(which='minor', length=2, width=1)
plt.setp(ax.spines.values(), linewidth=2)
plt.hist(np.abs(dec_icecat1_selected-dec_new_selected),align='left',bins=50)
plt.xlabel(r'|DEC$_{\mathrm{IceCat1}}$-DEC$_{\mathrm{new}}$| [deg]',size=14)
plt.ylabel(r'N',size=14)
#plt.xscale('log')
plt.yscale('log')
plt.grid()
plt.tight_layout()
output_path = 'output_plots/DEC_comparison.png'
plt.savefig(output_path)

# Step 2: Convert to SkyCoord
coords_icecat1    = SkyCoord(ra=ra_icecat1_selected, dec=dec_icecat1_selected, unit='deg')  # Add `unit='deg'` to specify the units
coords_new        = SkyCoord(ra=ra_new_selected, dec=dec_new_selected, unit='deg')  # Add `unit='deg'` to specify the units
#coords_icecat1    = SkyCoord(ra=ra_icecat1, dec=dec_icecat1, unit='deg')
#coords_new        = SkyCoord(ra=ra_new, dec=dec_new, unit='deg') 
#coords_icecat1    = SkyCoord(ra=ra_icecat1, dec=dec_icecat1, unit='deg')  # Add `unit='deg'` to specify the units
#coords_new        = SkyCoord(ra=ra_new, dec=dec_new, unit='deg')  # Add `unit='deg'` to specify the units

# Step 3: Plot the Equatorial Map
fig = plt.figure(figsize=(15, 10)) 
ax = plt.subplot(111, projection="mollweide")  # Mollweide projection for equatorial map

# Convert RA from degrees to radians and flip the direction for Mollweide
ra_rad_icecat1    = -coords_icecat1.ra.wrap_at(180 * u.deg).radian
dec_rad_icecat1   = coords_icecat1.dec.radian
ra_rad_new        = -coords_new.ra.wrap_at(180 * u.deg).radian
dec_rad_new       = coords_new.dec.radian

# Plot the points
ax.scatter(ra_rad_icecat1, dec_rad_icecat1, s=70, color='blue', alpha=0.5, label='IceCat-1 original')
ax.scatter(ra_rad_new, dec_rad_new, s=70, color='green', alpha=0.5, label='IceCat-1 with new reco')

# Define Galactic coordinates for the Galactic plane
l = np.linspace(0, 360, 1000)  # Galactic longitude
b = np.zeros_like(l)           # Galactic latitude = 0 (Galactic plane)
# Convert Galactic coordinates to Equatorial coordinates
galactic_coords = SkyCoord(l=l*u.degree, b=b*u.degree, frame='galactic')
equatorial_coords = galactic_coords.transform_to('icrs')
# Extract RA and Dec
ra = equatorial_coords.ra.wrap_at(180 * u.degree).degree  # Wrap RA to [-180, 180]
dec = equatorial_coords.dec.degree
plt.scatter(np.radians(ra), np.radians(dec), s=1, color='gray',alpha=0.5)

# Add grid with increased line width
ax.grid(True, linestyle='--', alpha=0.5, linewidth=1.5)  # Increased grid line width
# Increase axes line width
plt.setp(ax.spines.values(), linewidth=3.0)
# Add grid, labels, and title
ax.grid(True, linestyle='--', alpha=0.5)
ax.set_xticklabels(['14h', '16h', '18h', '20h', '22h', '0h', '2h', '4h', '6h', '8h', '10h'], fontsize=12)
ax.set_xlabel('Right Ascension', fontsize=18)
ax.set_ylabel('Declination', fontsize=18)
plt.title('Equatorial Sky Map', fontsize=18)
plt.legend(fontsize=14)
#output_path = 'output_plots/equatorial_map_icecat1.png'
#output_path = 'output_plots/equatorial_map_icecat1_old_common.png'
output_path = 'output_plots/equatorial_map_icecat1_new_common_tot.png'
plt.savefig(output_path, dpi=300)
print(f"Equatorial map saved to {output_path}")
