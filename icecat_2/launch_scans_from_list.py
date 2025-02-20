from pathlib import Path
import numpy as np
from icecube import dataio, icetray
from skymist.skyscan import SkyScan

import config
cfg = config.config()

def check_stream(infile):

    i3file = dataio.I3File(filepath)
    is_HED = False
    for frame in i3file:
        if frame.Stop == icetray.I3Frame.Physics:
            if frame.Has(cfg.key_passedfilters):
                streams = frame.Get(cfg.key_passedfilters)
                print(streams)
                if "HESE" in streams:
                    is_HED = True
            else:
                raise ValueError(f"The i3 file has not {cfg.key_passedfilters} in it!")
            if frame.Has("OnlineL2_SplineMPE_TruncatedEnergy_ORIG_Muon"):
                te_orig = frame.Get("OnlineL2_SplineMPE_TruncatedEnergy_ORIG_Muon")
                te_orig_value = te_orig.energy
                print(f"te_orig: {te_orig_value} GeV")
                if te_orig_value >= cfg.te_orig_threshold:
                    is_HED = True
            else:
                raise ValueError("The i3 file has not TE ORIG in it!")

    return is_HED

def launch_reco(filepath):

    is_HED=check_stream(filepath)

    if is_HED==True:
        reco = "millipede_wilks"
        njobs = 100
    else:
        reco = "splinempe"
        njobs = 10

    print(f"Event is HED: {is_HED}")
    print(f"Reco: {reco}, njobs: {njobs}")

    print("Launching scan ...")

    skyscan = SkyScan()

    skyscan.scan_file(
        Path(filepath),
        reco,
        "fine",
        njobs,
        "latest",
        additional_tag="icecat_test"
    )

'''
print('Old events')
infile = cfg.alerts_table_dir+"alerts_no_i3live.txt"
run, eventid = np.loadtxt(infile, usecols=(0,1), unpack=True, dtype=int)
for i in range(len(run)):
    print(f"Run: {run[i]}, EvtID: {eventid[i]}")
    filename='run'+str(run[i])+'_eventid'+str(eventid[i])+'_old_te.i3'
    filepath = cfg.i3files_dir + filename
    launch_reco(filepath)

print('Events from I3Live ...')
infile = cfg.alerts_table_dir+"alerts_i3live.txt"
run, eventid = np.loadtxt(infile, usecols=(0,1), unpack=True, dtype=int)
for i in range(len(run)):
    print(f"Run: {run[i]}, EvtID: {eventid[i]}")
    filename='run'+str(run[i])+'_eventid'+str(eventid[i])+'_i3live_te.i3'
    filepath = cfg.i3files_dir + filename
    launch_reco(filepath)
'''

infile = cfg.alerts_table_dir+"last_alerts.txt"
run, eventid, te_orig, evt_type, stream = np.loadtxt(infile, usecols=(0,1,2,3,4), unpack=True, dtype=str)
for i in range(len(run)):
    print(f"Run: {run[i]}, EvtID: {eventid[i]}")
    print(f"TE ORIG [TeV]: {te_orig[i]} --> evt_type: {evt_type[i]}")
    print(f"stream: {stream[i]}")
    filename='run'+str(run[i])+'_eventid'+str(eventid[i])+'_i3live_te.i3'
    filepath = cfg.i3files_dir + filename
    launch_reco(filepath)
