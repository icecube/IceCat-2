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

from icecube.realtime_tools import converter
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

def extract_truncated_energy_orig_alldoms_from_i3file(infile):

    frame_packet = load_frames(cfg.i3files_dir+infile)
    for f in frame_packet:
        if f.Stop == icetray.I3Frame.Physics:
            te_orig = f["OnlineL2_SplineMPE_TruncatedEnergy_AllDOMS_Muon"].energy

    return te_orig

def extract_time_from_i3file(infile):

    frame_packet = load_frames(cfg.i3files_dir+infile)
    for f in frame_packet:
        if f.Stop == icetray.I3Frame.Physics:
            time    = f["OnlineL2_SplineMPE_TruncatedEnergy_AllDOMS_Muon"].time

    return time

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
            l2_qtot = f['OnlineL2_HitStatisticsValuesIC'].q_tot_pulses

    return l2_qtot

print('Old events')
infile = cfg.alerts_table_dir+"alerts_no_i3live.csv"                                                                                                                  
run, eventid = np.loadtxt(infile, usecols=(0,1), unpack=True, dtype=int, delimiter=',')                                                                               
for i in range(len(run)):
    print(f"Run: {run[i]}, EvtID: {eventid[i]}")
    filename='run'+str(run[i])+'_eventid'+str(eventid[i])+'_old_pass2_te.i3'
    print(cfg.i3files_dir+filename)
    qtot            = extract_qtot_from_i3file(filename)
    te_alldoms      = extract_truncated_energy_orig_alldoms_from_i3file(filename)
    zenith, azimuth = extract_coordinates_from_i3file(filename)
    eventtime       = extract_time_from_i3file(filename)
    mjd             = converter.to_MJD(eventtime)
    ra_arr, dec_arr = astro.dir_to_equa(zenith, azimuth, mjd)
    ra, dec = ra_arr.item(), dec_arr.item()
    print(qtot, te_alldoms, zenith, azimuth)
    print(signalness(zenith, dec, qtot, te_alldoms))
