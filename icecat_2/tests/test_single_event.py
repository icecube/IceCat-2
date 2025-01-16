import numpy as np
import sys
import i3file_retriever
import get_truncated_energy_orig

import config
cfg = config.config()

run     = int(sys.argv[1])
eventid = int(sys.argv[2])

try:
    ## 1. Retrieve i3file for each event in the table from i3Live
    outfile='run'+str(run)+'_eventid'+str(eventid)+'_i3live.i3'
    i3file_retriever.retrieve_i3file(run,eventid,outfile)
    #outfile='run'+str(run)+'_eventid'+str(eventid)+'_err.i3'
    #i3file_retriever.retrieve_old_i3file(run,eventid,outfile)
    ## 2. Add OnlineL2_SplineMPE_TruncatedEnergy to the i3file
    get_truncated_energy_orig.add_truncated_energy_orig_i3file(run,eventid,'i3live')
    ## 3. Retrieve OnlineL2_SplineMPE_TruncatedEnergy_ORIG_Muon to check for each event if it is LED or HED
    ##    This difference will be crucial to define the reco algorithm to be launched (splinempe or millipede_wilks for LED and HED, respectively)
    infile='run'+str(run)+'_eventid'+str(eventid)+'_i3live_te.i3'
    te_orig = get_truncated_energy_orig.extract_truncated_energy_orig_from_i3file(infile)
    if(te_orig>=cfg.te_orig_threshold): evt_type='HED'
    if(te_orig<cfg.te_orig_threshold):  evt_type='LED'
    print(run,eventid,te_orig/1000,evt_type) ##print on terminal for checking purposes
except Exception as e:
    print(e)
    pass
