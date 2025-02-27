import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import config

# Load configuration
cfg = config.config()

# Load data efficiently with structured arrays
fields = ['run', 'evtid', 'teorig', 'evttype', 'stream']
dtype = [(field, int) if field in ['run', 'evtid'] else (field, float) if field == 'teorig' else (field, 'U10') for field in fields]

old_events = np.genfromtxt(
    cfg.alerts_table_dir + 'division_LED_HED_old_events.txt',
    usecols=(0, 1, 2, 3, 4),
    dtype=dtype
)

i3live_events = np.genfromtxt(
    cfg.alerts_table_dir + 'division_LED_HED_i3live_events.txt',
    usecols=(0, 1, 2, 3, 4),
    dtype=dtype
)

# Combine datasets
all_events = np.concatenate([old_events, i3live_events])

evts_splinempe = all_events[all_events['evttype']=='LED']
evts_millipedewilks = all_events[all_events['evttype']=='HED']

print(len(evts_splinempe))
print(len(evts_millipedewilks))

# Filter based on condition
new_alerts = all_events[all_events['run'] >= 138487]
icecat1_alerts = all_events[all_events['run'] < 138487]

print(f"Number of old evts (no i3Live) = {len(old_events)}")
print(f"Number of evts on i3Live      = {len(i3live_events)}")
print(f"-----------------------------  = {len(all_events)}")
print(f"Number of evts from IceCat-1  = {len(icecat1_alerts)}")
print(f"Number of new realtime alerts = {len(new_alerts)}")

# Extract teorig arrays for plotting
teorig_all = all_events['teorig']
teorig_icecat1 = icecat1_alerts['teorig']
teorig_new = new_alerts['teorig']

# Plot histogram
fig, ax = plt.subplots(figsize=(7, 4))
ax.tick_params(axis='y', labelsize=14, width=1, length=4)
ax.tick_params(axis='x', labelsize=14, width=1, length=4)
ax.tick_params(which='minor', length=2, width=1)
plt.setp(ax.spines.values(), linewidth=2)

bins = np.logspace(np.log10(teorig_all.min()), np.log10(teorig_all.max()), 50)
plt.hist(teorig_icecat1, bins=bins, histtype='step', lw=6, align='left', label=f'IceCat-1 (N={len(teorig_icecat1)})')
plt.hist(teorig_new, bins=bins, histtype='step', lw=6, align='left', label=f'New alerts (N={len(teorig_new)})', color='green')
plt.hist(teorig_all, bins=bins, histtype='step', lw=6, align='left', label=f'All alerts, IceCat-2 (N={len(teorig_all)})', color='black') # 
plt.axvline(cfg.te_orig_threshold * 1e-3, lw=2.5, color='red', label=r'E$_{\mathrm{threshold}}$=50 TeV', linestyle='--')
plt.xlabel(r'Truncated Energy ORIG [TeV]', size=14)
#plt.yscale('log')
plt.xscale('log')
plt.ylabel('N', size=14)
plt.grid()
plt.legend(fontsize=12)
plt.tight_layout()

# Save the plot
output_path = 'output_plots/te_orig.png'
plt.savefig(output_path, dpi=300)
print(f"Plot saved to {output_path}")

# Load the data into a DataFrame
file_path_icecat1 = cfg.alerts_table_dir + 'IceCat-1-dataverse_files/IceCube_Gold_Bronze_Tracks.csv'  # Replace with the correct path
data_icecat1 = pd.read_csv(file_path_icecat1)
# Ensure the 'start' column is read as datetime
data_icecat1['START'] = pd.to_datetime(data_icecat1['START'])
# Sort the data by the 'start' column to simulate time progression
data_icecat1 = data_icecat1.sort_values('START')
# Create a cumulative count column
data_icecat1['cumulative_count'] = range(1, len(data_icecat1) + 1)

file_path_amon_gold_bronze = cfg.alerts_table_dir + 'amon_tables/amon_table_gold_bronze.csv'
data_amon_gold_bronze = pd.read_csv(file_path_amon_gold_bronze)
data_amon_gold_bronze['DateTime'] = pd.to_datetime(data_amon_gold_bronze['DateTime'])
data_amon_gold_bronze = data_amon_gold_bronze.sort_values('DateTime')
data_new = data_amon_gold_bronze[data_amon_gold_bronze['Run'] >= 138487]
data_new = data_new[data_new['Rev'] == 0]
data_new['cumulative_count'] = range(1, len(data_new) + 1) + data_icecat1['cumulative_count'].iloc[-1]

bronze_new = data_new[data_new['Notice'] == 'BRONZE']
gold_new = data_new[data_new['Notice'] == 'GOLD']

gold_icecat1 = data_icecat1[
    (data_icecat1['I3TYPE'] == 'gfu-gold') | 
    (data_icecat1['I3TYPE'] == 'hese-gold') | 
    (data_icecat1['I3TYPE'] == 'ehe-gold')
]
bronze_icecat1 = data_icecat1[
    (data_icecat1['I3TYPE'] == 'gfu-bronze') | 
    (data_icecat1['I3TYPE'] == 'hese-bronze')
]

far_gold_icecat1   = gold_icecat1['FAR']
far_bronze_icecat1 = bronze_icecat1['FAR']
far_gold_new       = gold_new['FAR']
far_bronze_new     = bronze_new['FAR']

fig, ax = plt.subplots(figsize=(7, 4))
ax.tick_params(axis='y', labelsize=14, width=1, length=4)
ax.tick_params(axis='x', labelsize=14, width=1, length=4)
ax.tick_params(which='minor', length=2, width=1)
plt.setp(ax.spines.values(), linewidth=2)
plt.hist(far_gold_icecat1, bins=25, range=(0,5), alpha=0.7, histtype='stepfilled', lw=6, align='left', color='gold', label='Gold (IceCat-1)')
plt.hist(far_bronze_icecat1, bins=25, range=(0,5), alpha=0.7, histtype='stepfilled', lw=6, align='left', color='darkgoldenrod', label='Bronze (IceCat-1)')
plt.hist(far_gold_new, bins=25, range=(0,5), alpha=0.7, histtype='stepfilled', lw=6, align='left', color='green', label='Gold (New alerts)')
plt.hist(far_bronze_new, bins=25, range=(0,5), alpha=0.7, histtype='stepfilled', lw=6, align='left', color='red', label='Bronze (New alerts)')
plt.xlabel(r'FAR [yr$^{-1}$]', size=14)
#plt.yscale('log')
plt.ylabel('N', size=14)
plt.grid()
plt.legend(fontsize=12)
plt.tight_layout()
output_path = 'output_plots/FAR.png'
plt.savefig(output_path,dpi=300)
print(f"Plot saved to {output_path}")

sig_gold_icecat1   = gold_icecat1['SIGNAL']
sig_bronze_icecat1 = bronze_icecat1['SIGNAL']
sig_gold_new       = gold_new['Signalness']
sig_bronze_new     = bronze_new['Signalness']

fig, ax = plt.subplots(figsize=(7, 4))
ax.tick_params(axis='y', labelsize=14, width=1, length=4)
ax.tick_params(axis='x', labelsize=14, width=1, length=4)
ax.tick_params(which='minor', length=2, width=1)
plt.setp(ax.spines.values(), linewidth=2)
plt.hist(sig_gold_icecat1, bins=25, range=(0,1), alpha=0.7, histtype='stepfilled', lw=6, align='left', color='gold', label='Gold (IceCat-1)')
plt.hist(sig_bronze_icecat1, bins=25, range=(0,1), alpha=0.7, histtype='stepfilled', lw=6, align='left', color='darkgoldenrod', label='Bronze (IceCat-1)')
plt.hist(sig_gold_new, bins=25, range=(0,1), alpha=0.7, histtype='stepfilled', lw=6, align='left', color='green', label='Gold (New alerts)')
plt.hist(sig_bronze_new, bins=25, range=(0,1), alpha=0.7, histtype='stepfilled', lw=6, align='left', color='red', label='Bronze (New alerts)')
plt.xlabel(r'Signalness', size=14)
#plt.yscale('log')
plt.ylabel('N', size=14)
plt.grid()
plt.legend(fontsize=12)
plt.tight_layout()
output_path = 'output_plots/signalness.png'
plt.savefig(output_path)
print(f"Plot saved to {output_path}")

bronze_icecat1.loc[:, 'cumulative_count'] = range(1, len(bronze_icecat1) + 1)
gold_icecat1.loc[:, 'cumulative_count'] = range(1, len(gold_icecat1) + 1)
bronze_new.loc[:, 'cumulative_count'] = range(1, len(bronze_new) + 1) + bronze_icecat1['cumulative_count'].iloc[-1]
gold_new.loc[:, 'cumulative_count'] = range(1, len(gold_new) + 1) + gold_icecat1['cumulative_count'].iloc[-1]

'''
fig, ax = plt.subplots(figsize=(10, 6))
ax.tick_params(axis='y', labelsize=14, width=1, length=4)
ax.tick_params(axis='x', labelsize=14, width=1, length=4)
ax.tick_params(which='minor', length=2, width=1)
plt.setp(ax.spines.values(), linewidth=2)
# Customize x-axis with year formatting
ax.xaxis.set_major_locator(mdates.YearLocator(1))  # Set major ticks at yearly intervals
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # Format ticks as year (e.g., 2020, 2021)
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
ax.plot(data_icecat1['START'], data_icecat1['cumulative_count'], label=r'All (N=%i)' %len(data_icecat1['cumulative_count']), lw=2.5, color='black')
ax.plot(data_new['DateTime'], data_new['cumulative_count'], lw=2.5, color='black', linestyle='-')
ax.plot(gold_icecat1['START'], gold_icecat1['cumulative_count'], label=r'Gold (N=%i)' %len(gold_icecat1['cumulative_count']), lw=2.5, color='gold')
ax.plot(bronze_icecat1['START'], bronze_icecat1['cumulative_count'], label=r'Bronze (N=%i)' %len(bronze_icecat1['cumulative_count']), lw=2.5, color='darkgoldenrod')
ax.plot(gold_new['DateTime'], gold_new['cumulative_count'], lw=2.5, color='gold', linestyle='-')
ax.plot(bronze_new['DateTime'], bronze_new['cumulative_count'], lw=2.5, color='darkgoldenrod')
plt.axvspan(data_new['DateTime'].iloc[0], data_new['DateTime'].iloc[-1], linestyle='-', alpha=0.4, color='green', label='New realtime alerts (N=%i, N$_{\mathrm{gold}}$=%i, N$_{\mathrm{bronze}}$=%i)' %(len(new_alerts),len(gold_new),len(bronze_new)))
plt.xlabel('Time', fontsize=14)
plt.ylabel('Cumulative Alerts', fontsize=14)
plt.grid()
plt.legend(fontsize=15)
plt.tight_layout()
output_path_cumulative = 'output_plots/cumulative_events_vs_time_withpoisson.png'
plt.savefig(output_path_cumulative)
print(f"Cumulative plot saved to {output_path_cumulative}")
'''

# Combine the START times from both data_icecat1 and data_new
combined_start = pd.concat([data_icecat1['START'], data_new['DateTime']])
# Sort combined timestamps to ensure chronological order
combined_start_sorted = combined_start.sort_values()
# Define the new start time as the earliest timestamp from the combined data
start_time_combined = combined_start_sorted.min()
# Calculate the elapsed time for both datasets based on the new start time
elapsed_years_combined = (combined_start_sorted - start_time_combined).dt.total_seconds() / (365.25 * 24 * 60 * 60)

# Calculate event rates (average number of events per year)
rate_all = (len(data_icecat1)+len(data_new)) / elapsed_years_combined.max()  # Rate for all events
rate_gold = (len(gold_icecat1)+len(gold_new)) / elapsed_years_combined.max()  # Rate for gold events
rate_bronze = (len(bronze_icecat1)+len(bronze_new)) / elapsed_years_combined.max()  # Rate for bronze events

# Compute cumulative Poisson expectations
expected_all = rate_all * elapsed_years_combined
expected_gold = rate_gold * elapsed_years_combined
expected_bronze = rate_bronze * elapsed_years_combined

# Print the rates for debugging
print(f"Rate (All): {rate_all:.2f} events/year")
print(f"Rate (Gold): {rate_gold:.2f} events/year")
print(f"Rate (Bronze): {rate_bronze:.2f} events/year")
# Ensure 'df' and the expected values are correctly defined
# 'df' contains the 'START' datetime column used for plotting Poisson expectations

fig, ax = plt.subplots(figsize=(10, 6))
ax.tick_params(axis='y', labelsize=14, width=1, length=4)
ax.tick_params(axis='x', labelsize=14, width=1, length=4)
ax.tick_params(which='minor', length=2, width=1)
plt.setp(ax.spines.values(), linewidth=2)
ax.xaxis.set_major_locator(mdates.YearLocator(1))  # Set major ticks at yearly intervals
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # Format ticks as year (e.g., 2020, 2021)
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability

# Plot cumulative counts
ax.plot(data_icecat1['START'], data_icecat1['cumulative_count'], 
        label=r'All (N=%i)' % len(data_icecat1['cumulative_count']), lw=2.5, color='black')
ax.plot(data_new['DateTime'], data_new['cumulative_count'], 
        lw=2.5, color='black', linestyle='-')
ax.plot(gold_icecat1['START'], gold_icecat1['cumulative_count'], 
        label=r'Gold (N=%i)' % len(gold_icecat1['cumulative_count']), lw=2.5, color='gold')
ax.plot(bronze_icecat1['START'], bronze_icecat1['cumulative_count'], 
        label=r'Bronze (N=%i)' % len(bronze_icecat1['cumulative_count']), lw=2.5, color='darkgoldenrod')
ax.plot(gold_new['DateTime'], gold_new['cumulative_count'], 
        lw=2.5, color='gold', linestyle='-')
ax.plot(bronze_new['DateTime'], bronze_new['cumulative_count'], 
        lw=2.5, color='darkgoldenrod')

# Add Poisson expectations
ax.plot(combined_start_sorted, expected_all, 'k--', label='Poisson Expectations')
ax.plot(combined_start_sorted, expected_gold, 'y--')
ax.plot(combined_start_sorted, expected_bronze, 'brown', linestyle='--')

plt.axvspan(data_new['DateTime'].iloc[0], data_new['DateTime'].iloc[-1], 
            linestyle='-', alpha=0.4, color='green', 
            label='New realtime alerts (N=%i, N$_{\mathrm{gold}}$=%i, N$_{\mathrm{bronze}}$=%i)' %
                  (len(new_alerts), len(gold_new), len(bronze_new)))

plt.xlabel('Time', fontsize=14)
plt.ylabel('Cumulative Alerts', fontsize=14)
plt.grid()
plt.legend(fontsize=13)
plt.tight_layout()
output_path_cumulative = 'output_plots/cumulative_events_vs_time_withpoisson.png'
plt.savefig(output_path_cumulative,dpi=300)
print(f"Cumulative plot saved to {output_path_cumulative}")
