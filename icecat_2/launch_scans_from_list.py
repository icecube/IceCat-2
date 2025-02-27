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
            if frame.Has("Streams"):
                streams = frame.Get("Streams")
                print(streams)
                if "HESE" in streams:
                    is_HED = True
            else:
                raise ValueError("The i3 file has not Streams in it!")
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
        additional_tag="icecat_test"
    )

'''
print('Old events')
infile = cfg.alerts_table_dir+"alerts_no_i3live.txt"
run, eventid = np.loadtxt(infile, usecols=(0,1), unpack=True, dtype=int)
for i in range(len(run)):
    print(f"Run: {run[i]}, EvtID: {eventid[i]}")
    filename='run'+str(run[i])+'_eventid'+str(eventid[i])+'_old_te.i3'
    #filepath = cfg.i3files_dir + filename
    filepath = '/data/user/gsommani/IceCat-2/output/'+filename
    launch_reco(filepath)
    time.sleep(5)
'''

infile = "evts_without_scan_28Jan.txt"
run, eventid = np.loadtxt(infile, usecols=(0,1), unpack=True, dtype=int)
pattern = r'\((-?\d+\.?\d*)\)'
#for i in range(len(run)):
Nmin=101
N=100
for i in range(Nmin,N+1):
    print(f"Run: {run[i]}, EvtID: {eventid[i]}")
    filename_i3live = 'run'+str(run[i])+'_eventid'+str(eventid[i])+'_i3live_te.i3'
    filename_old    = 'run'+str(run[i])+'_eventid'+str(eventid[i])+'_old_te.i3'
    #filepath = cfg.i3files_dir + filename                                                                                   
    base_path = '/data/user/gsommani/IceCat-2/output/'
    if os.path.exists(base_path + filename_i3live):
        filepath = base_path + filename_i3live
    elif os.path.exists(base_path + filename_old):
        filepath = base_path + filename_old
    else:
        print(f"Neither file exists for Run: {run[i]}, EvtID: {eventid[i]}")
        continue
    launch_reco(filepath)
    time.sleep(10)

quit()

print('Events from I3Live ...')
infile = cfg.alerts_table_dir+"alerts_i3live.txt"
run, eventid = np.loadtxt(infile, usecols=(0,1), unpack=True, dtype=int)
infile_last = cfg.alerts_table_dir+"last_alerts.txt"
run_last, eventid_last = np.loadtxt(infile_last, usecols=(0,1), unpack=True, dtype=str)
for i in range(len(run)):
    check_run = 0
    for j in range(len(run_last)):
        if(run[i]==run_last[j]): check_run = 1
    if(check_run==0):
        print(f"Run: {run[i]}, EvtID: {eventid[i]}")
        filename='run'+str(run[i])+'_eventid'+str(eventid[i])+'_i3live_te.i3'
        #filepath = cfg.i3files_dir + filename
        filepath = '/data/user/gsommani/IceCat-2/output/'+filename
        launch_reco(filepath)
    time.sleep(10)

infile = cfg.alerts_table_dir+"last_alerts.txt"
run, eventid, te_orig, evt_type, stream = np.loadtxt(infile, usecols=(0,1,2,3,4), unpack=True, dtype=str)
for i in range(len(run)):
    print(f"Run: {run[i]}, EvtID: {eventid[i]}")
    print(f"TE ORIG [TeV]: {te_orig[i]} --> evt_type: {evt_type[i]}")
    print(f"stream: {stream[i]}")
    filename='run'+str(run[i])+'_eventid'+str(eventid[i])+'_i3live_te.i3'
    filepath = cfg.i3files_dir + filename
    launch_reco(filepath)
