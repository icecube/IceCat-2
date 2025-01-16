import numpy as np
import sys
import i3file_retriever
import add_truncated_energy_i3files

import config
cfg = config.config()

#infile = cfg.alerts_table_dir+"AlertsList_tot.txt"
infile = cfg.alerts_table_dir+"alerts_i3live.txt"
run, eventid = np.loadtxt(infile, usecols=(0,1), unpack=True, dtype=str)

print('# run evtid TE_ORIG[TeV] evttype')
for i in range(len(run)):
    try:
        ## 1. Retrieve i3file for each event in the table from i3Live
        outfile='run'+str(run[i])+'_eventid'+str(eventid[i])+'_i3live.i3'
        i3file_retriever.retrieve_i3file(int(run[i]),int(eventid[i]),outfile)
        ## 2. Add OnlineL2_SplineMPE_TruncatedEnergy to the i3file
        add_truncated_energy_i3files.add_truncated_energy_i3file(int(run[i]),int(eventid[i]),'i3live')
        ## 3. Retrieve OnlineL2_SplineMPE_TruncatedEnergy_ORIG_Muon to check for each event if it is LED or HED
        ##    This difference will be crucial to define the reco algorithm to be launched (splinempe or millipede_wilks for LED and HED, respectively)
        infile='run'+str(run[i])+'_eventid'+str(eventid[i])+'_i3live_te.i3'
        te_orig = add_truncated_energy_i3files.extract_truncated_energy_orig_muon_from_i3file(infile)
        if(te_orig>=cfg.te_orig_threshold): evt_type='HED'
        if(te_orig<cfg.te_orig_threshold):  evt_type='LED'
        print(run[i],eventid[i],te_orig/1000,evt_type) ##print on terminal for checking purposes
    except Exception as e:
        print(e)
        pass
