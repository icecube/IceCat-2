import numpy as np
import os
from os.path import isfile, join

from icecube.icetray import I3Tray, I3Units, I3Frame
from icecube import (
    dataclasses,
    icetray,
    dataio,
    astro,
    recclasses, ## needed for I3HitStatisticsValues
)

#from icecube.realtime_tools import converter
from icecube.realtime_gfu.muon_alerts import signalness, neutrino_energy

import config
cfg = config.config()

def load_frames(infile):
    frame_packet = []
    i3f = dataio.I3File(infile)
    while True:
       if not i3f.more():
          return frame_packet
       frame = i3f.pop_frame()
       frame_packet.append(frame)

def extract_truncated_energies_from_i3file(infile):

    frame_packet = load_frames(cfg.i3files_dir+infile)
    for f in frame_packet:
        if f.Stop == icetray.I3Frame.Physics:
            te_alldoms = f["OnlineL2_SplineMPE_TruncatedEnergy_AllDOMS_Muon"].energy
            te_orig    = f["OnlineL2_SplineMPE_TruncatedEnergy_ORIG_Muon"].energy

    return te_alldoms, te_orig


def extract_time_from_i3file(infile):

    frame_packet = load_frames(cfg.i3files_dir+infile)
    for f in frame_packet:
        if f.Stop == icetray.I3Frame.Physics:
            starttime = f['I3EventHeader'].start_time
            mjd       = f['I3EventHeader'].start_time.mod_julian_day_double

    return starttime, mjd

def extract_coordinates_from_i3file(infile):

    frame_packet = load_frames(cfg.i3files_dir+infile)
    for f in frame_packet:
        if f.Stop == icetray.I3Frame.Physics:
            zenith = f["OnlineL2_SplineMPE"].dir.zenith
            azimuth = f["OnlineL2_SplineMPE"].dir.azimuth

    return zenith, azimuth

def extract_qtot_from_i3file(infile):

    frame_packet = load_frames(cfg.i3files_dir+infile)

    for f in frame_packet:
        if f.Stop == icetray.I3Frame.Physics:
            if 'OnlineL2_HitStatisticsValuesIC' in f:
                return f['OnlineL2_HitStatisticsValuesIC'].q_tot_pulses
            elif 'AlertShortFollowupMsg' in f:
                alert_json = f['AlertShortFollowupMsg'].value
                alert_data = json.loads(alert_json)
                return alert_data.get('qtot')

print('run, evtid, ra, dec, zenith, azimuth, qtot, te_alldoms, te_orig, nu_energy, signalness')

##########################

def extract_info(run,eventid):

    filename_old   = f'run{run}_eventid{eventid}_old_pass2_te.i3'
    filename_i3live = f'run{run}_eventid{eventid}_i3live_pass2_te.i3'

    filepath_old = os.path.join(cfg.i3files_dir, filename_old)
    filepath_i3live = os.path.join(cfg.i3files_dir, filename_i3live)

    if os.path.exists(filepath_old):
        filename = filename_old
    elif os.path.exists(filepath_i3live):
        filename = filename_i3live
    else:
        raise FileNotFoundError(f"No suitable i3 file found for run {run} and event ID {eventid}.")

    qtot                 = extract_qtot_from_i3file(filename)
    te_alldoms, te_orig  = extract_truncated_energies_from_i3file(filename)
    zenith, azimuth      = extract_coordinates_from_i3file(filename)
    eventtime, mjd       = extract_time_from_i3file(filename)
    # the way below returns the same result (tested)
    #mjd                  = converter.to_MJD(eventtime)
    #print(eventtime, mjd_1, mjd)
    ra_arr, dec_arr      = astro.dir_to_equa(zenith, azimuth, mjd)
    ra, dec              = ra_arr.item(), dec_arr.item()

    nu_energy  = neutrino_energy(te_alldoms)
    sig        = signalness(zenith, dec, qtot, te_alldoms)[0]

    print(run, eventid, round(ra,3), round(dec,3), round(zenith,3), round(azimuth,3), round(qtot,3), round(te_alldoms,3), round(te_orig,3), round(nu_energy,3), round(sig,3))

infile = cfg.alerts_table_dir+"alerts_no_i3live.csv"                
run, eventid = np.loadtxt(infile, usecols=(0,1), unpack=True, dtype=int, delimiter=',')
for i in range(len(run)):    
    extract_info(str(run[i]),str(eventid[i]))

infile = cfg.alerts_table_dir+"alerts_i3live.csv"
run, eventid = np.loadtxt(infile, usecols=(0,1), unpack=True, dtype=int, delimiter=',')
for i in range(len(run)):
    extract_info(str(run[i]),str(eventid[i]))
