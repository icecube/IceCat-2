import time
from pathlib import Path
import numpy as np
from icecube import dataio, icetray
from skymist.skyscan import SkyScan

import config
cfg = config.config()

def launch_reco_output(run,eventid,reco_algo,scan_id):

    print(f"Run = %i, EventID = %i" %(run,eventid))


    led_hed=False
    angular_error_floor=None
    if(reco_algo=='splinempe'):
        if(run>=140033):
            led_hed=True
        else:
            angular_error_floor=0.2
    try:
        api = SkyScan()
        api.plot(
            scan_id=scan_id,
            led_hed=led_hed,
            systematics=False,
            plot_4fgl=True,
            angular_error_floor=angular_error_floor,
            llh_map=False,
            #llh_map=True,
        )
    except Exception as e:
        print(e)
        pass


infile = cfg.alerts_table_dir+"scans_completed_old_evts.txt"
run, eventid = np.loadtxt(infile, usecols=(0,1), unpack=True, dtype=int)
reco_algo, scan_id = np.loadtxt(infile, usecols=(2,3), unpack=True, dtype=str)
for i in range(len(run)):
    launch_reco_output(run[i],eventid[i],reco_algo[i],scan_id[i])
    time.sleep(5)

infile = cfg.alerts_table_dir+"scans_completed_i3live_evts.txt"
run, eventid      = np.loadtxt(infile, usecols=(0,1), unpack=True, dtype=int)
reco_algo, scan_id = np.loadtxt(infile, usecols=(2,3), unpack=True, dtype=str)
for i in range(len(run)):
    launch_reco_output(run[i],eventid[i],reco_algo[i],scan_id[i])
    time.sleep(5)
