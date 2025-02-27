import glob
import os

from icecube import (
    dataio,
    icetray,
)
from icecube.icetray import I3Tray

import config
cfg = config.config()
path = cfg.old_alerts_path

files = sorted(glob.glob(path+"*.*"))

for file_i in files:

    #print('Checking ', file_i)
    input_i3file = dataio.I3File(file_i)
    for frame in input_i3file:
        if frame.Stop == icetray.I3Frame.Stream('p'):
            sub_evtid = frame["I3EventHeader"].sub_event_id
            #print('sub_event_id = ', sub_evtid)
            if(sub_evtid != 0):
                #print('ACHTUNG!!!')
                print(file_i, sub_evtid)
            break
            