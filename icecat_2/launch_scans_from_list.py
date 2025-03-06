import time
from pathlib import Path
import numpy as np
from icecube import dataio, icetray
from skymist.skyscan import SkyScan
import os
import config
cfg = config.config()

def check_stream(infile):

    i3file = dataio.I3File(filepath)
    is_HED = False
    for frame in i3file:
        if frame.Stop == icetray.I3Frame.Physics:
            if frame.Has("AlertNamesPassed_IceCat2"):
                streams = frame.Get("AlertNamesPassed_IceCat2")
                print(streams)
                if "HESE" in streams:
                    is_HED = True
            else:
                raise ValueError("The i3 file has not AlertNamesPassed_IceCat2 in it!")
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
        njobs = 100

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
        additional_tag="icecat_gdcpass2"
    )


print('Old events')
infile = cfg.alerts_table_dir+"alerts_no_i3live.csv"
run, eventid = np.loadtxt(infile, usecols=(0,1), unpack=True, dtype=int, delimiter=',')
for i in range(len(run)):
    print(f"Run: {run[i]}, EvtID: {eventid[i]}")
    filename='run'+str(run[i])+'_eventid'+str(eventid[i])+'_old_pass2_te.i3'
    #filename='run'+str(run[i])+'_eventid'+str(eventid[i])+'_old_te.i3'
    filepath = cfg.i3files_dir + filename
    print(filepath)
    launch_reco(filepath)
    time.sleep(10)

print('Events from I3Live ...')
infile = cfg.alerts_table_dir+"alerts_i3live.csv"
run, eventid = np.loadtxt(infile, usecols=(0,1), unpack=True, dtype=int, delimiter=',')
for i in range(len(run)):
    check_run = 0
    for j in range(len(run_last)):
        if(run[i]==run_last[j]): check_run = 1
    if(check_run==0):
        print(f"Run: {run[i]}, EvtID: {eventid[i]}")
        filename='run'+str(run[i])+'_eventid'+str(eventid[i])+'_i3live_pass2_te.i3'
        #filename='run'+str(run[i])+'_eventid'+str(eventid[i])+'_i3live_te.i3'
        filepath = cfg.i3files_dir + filename
        launch_reco(filepath)
    time.sleep(10)
