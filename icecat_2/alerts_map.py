import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.coordinates import SkyCoord
from astropy.visualization import astropy_mpl_style
import config
cfg = config.config()
from astropy import units as u

plt.style.use(astropy_mpl_style)  # Optional for better styling

# Step 1: Read CSV file
file_path = cfg.alerts_table_dir+'IceCat-1-dataverse_files/IceCube_Gold_Bronze_Tracks.csv'  
data_icecat1 = pd.read_csv(file_path)
data_gold_icecat1 = data_icecat1[
    (data_icecat1['I3TYPE'] == 'gfu-gold') | 
    (data_icecat1['I3TYPE'] == 'hese-gold') | 
    (data_icecat1['I3TYPE'] == 'ehe-gold')
]
data_bronze_icecat1 = data_icecat1[
    (data_icecat1['I3TYPE'] == 'gfu-bronze') | 
    (data_icecat1['I3TYPE'] == 'hese-bronze')
]

file_path = cfg.alerts_table_dir+'output_reco.csv'  
data_new = pd.read_csv(file_path)
file_path_amon_gold_bronze = cfg.alerts_table_dir + 'amon_tables/amon_table_gold_bronze.csv'
data_amon_gold_bronze = pd.read_csv(file_path_amon_gold_bronze)
data_amon_gold = data_amon_gold_bronze[data_amon_gold_bronze['Notice']=='GOLD']
data_amon_bronze = data_amon_gold_bronze[data_amon_gold_bronze['Notice']=='BRONZE']
data_amon_gold   = data_amon_gold[data_amon_gold['Rev']==1]
data_amon_bronze = data_amon_bronze[data_amon_bronze['Rev']==1]
#  New alerts start from the gold alert of the 27th October 2023, with RUNID=138487 and EVENTNUM=60138479. 
data_gold_new   = data_amon_gold[data_amon_gold['Run']>138487]
data_bronze_new = data_amon_bronze[data_amon_bronze['Run']>138487]

# Ensure RA and Dec columns are correctly named and in degrees
ra_gold_icecat1    = data_gold_icecat1['RA']  # Replace with the column name for Right Ascension
dec_gold_icecat1   = data_gold_icecat1['DEC']  # Replace with the column name for Declination
ra_bronze_icecat1  = data_bronze_icecat1['RA']  # Replace with the column name for Right Ascension
dec_bronze_icecat1 = data_bronze_icecat1['DEC']  # Replace with the column name for Declination
ra_gold_new        = data_gold_new['RA']  # Replace with the column name for Right Ascension
dec_gold_new       = data_gold_new['Dec']  # Replace with the column name for Declination
ra_bronze_new      = data_bronze_new['RA']  # Replace with the column name for Right Ascension
dec_bronze_new     = data_bronze_new['Dec']  # Replace with the column name for Declination

# Step 2: Convert to SkyCoord
coords_gold_icecat1    = SkyCoord(ra=ra_gold_icecat1, dec=dec_gold_icecat1, unit='deg')  # Add `unit='deg'` to specify the units
coords_bronze_icecat1  = SkyCoord(ra=ra_bronze_icecat1, dec=dec_bronze_icecat1, unit='deg')  # Add `unit='deg'` to specify the units
coords_gold_new        = SkyCoord(ra=ra_gold_new, dec=dec_gold_new, unit='deg')  # Add `unit='deg'` to specify the units
coords_bronze_new      = SkyCoord(ra=ra_bronze_new, dec=dec_bronze_new, unit='deg')  # Add `unit='deg'` to specify the units

# Step 3: Plot the Equatorial Map
fig = plt.figure(figsize=(15, 10)) 
ax = plt.subplot(111, projection="mollweide")  # Mollweide projection for equatorial map

# Convert RA from degrees to radians and flip the direction for Mollweide
ra_rad_gold_icecat1    = -coords_gold_icecat1.ra.wrap_at(180 * u.deg).radian
dec_rad_gold_icecat1   = coords_gold_icecat1.dec.radian
ra_rad_bronze_icecat1  = -coords_bronze_icecat1.ra.wrap_at(180 * u.deg).radian
dec_rad_bronze_icecat1 = coords_bronze_icecat1.dec.radian
ra_rad_gold_new        = -coords_gold_new.ra.wrap_at(180 * u.deg).radian
dec_rad_gold_new       = coords_gold_new.dec.radian
ra_rad_bronze_new      = -coords_bronze_new.ra.wrap_at(180 * u.deg).radian
dec_rad_bronze_new     = coords_bronze_new.dec.radian

# Define Galactic coordinates for the Galactic plane
l = np.linspace(0, 360, 1000)  # Galactic longitude
b = np.zeros_like(l)           # Galactic latitude = 0 (Galactic plane)
# Convert Galactic coordinates to Equatorial coordinates
galactic_coords = SkyCoord(l=l*u.degree, b=b*u.degree, frame='galactic')
equatorial_coords = galactic_coords.transform_to('icrs')
# Extract RA and Dec
ra = equatorial_coords.ra.wrap_at(180 * u.degree).degree  # Wrap RA to [-180, 180]
dec = equatorial_coords.dec.degree
plt.scatter(np.radians(ra), np.radians(dec), s=0.5, color='gray',alpha=0.3)

# Plot the points
ax.scatter(ra_rad_gold_icecat1, dec_rad_gold_icecat1, s=70, color='gold', alpha=0.5, label='Gold (IceCat-1)')
ax.scatter(ra_rad_bronze_icecat1, dec_rad_bronze_icecat1, s=70, color='darkgoldenrod', alpha=0.6, label='Bronze (IceCat-1)')
ax.scatter(ra_rad_gold_new, dec_rad_gold_new, s=70, color='red', alpha=1, label='Gold (New alerts)', marker='x')
ax.scatter(ra_rad_bronze_new, dec_rad_bronze_new, s=70, color='green', alpha=1, label='Bronze (New alerts)', marker='x')

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
output_path = 'output_plots/equatorial_map_withgalacticplane.png'
plt.savefig(output_path, dpi=300)
#plt.savefig(output_path)
print(f"Equatorial map saved to {output_path}")