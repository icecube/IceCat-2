import time
import re
import numpy as np
from icecube import dataio, icetray
from skymist.skydriver import SkyDriverREST
from skymist.skyscan import SkyScan
import pandas as pd

import config
cfg = config.config()

def take_completed_scans():

    run_completed_old, evtid_completed_old       = np.loadtxt(cfg.alerts_table_dir+'scans_completed_old_evts.txt', unpack=True, usecols=(0,1), dtype=int)
    run_completed_i3live, evtid_completed_i3live = np.loadtxt(cfg.alerts_table_dir+'scans_completed_i3live_evts.txt', unpack=True, usecols=(0,1), dtype=int)

    run_completed_all   = np.setdiff1d(run_completed_old, run_completed_i3live)
    evtid_completed_all = np.setdiff1d(evtid_completed_old, evtid_completed_i3live)

    run_completed_all   = np.concatenate((run_completed_old,run_completed_i3live), axis=0)
    evtid_completed_all = np.concatenate((evtid_completed_old,evtid_completed_i3live), axis=0)

    return run_completed_all, evtid_completed_all

def delete_scans(run_list, eventid_list, additional_tag):

    api = SkyDriverREST()
    skyscan = SkyScan()
    pattern = r'\((-?\d+\.?\d*)\)'
    for i in range(len(run_list)):
        print(int(run_list[i]),int(eventid_list[i]))
        scan_id = []
        scan_list = skyscan.list_scans(int(run_list[i]),int(eventid_list[i]))
        df = pd.DataFrame(scan_list)
        for j in range(len(df)):
            if(df.iloc[j]['additional_tag']==additional_tag):
                scan_id.append(df.iloc[j]['id'])
                #scan_id   = df.iloc[j]['id']
                #progress  = float(re.findall(pattern, df.iloc[j]['progress'])[0])*100
                #if(float(progress)<100.): result = api.delete(scan_id, force=False)
        if(len(scan_id)>1):
            print(len(scan_id))
            print(scan_id)
            for k in range(len(scan_id)-1):
                print(scan_id[k])
                try:
                    result = api.delete(scan_id[k], force=True)
                except Exception as e:
                    print(e)
                    pass
        time.sleep(10)

import time
import pandas as pd
import re

def check_progress_scan(run_list, eventid_list, additional_tag, tag_file=None, outputfile=False):
    
    #run_completed_all, evtid_completed_all = take_completed_scans()
    skyscan = SkyScan()
    pattern = r'\((-?\d+\.?\d*)\)'

    f1 = f2 = f3 = None
    if outputfile:
        f1 = open(f"evts_without_scan{tag_file}.txt", "a")
        f2 = open(f"scans_completed{tag_file}.txt", "a")
        f3 = open(f"scans_inprogress{tag_file}.txt", "a")

    for i, (run, evtid) in enumerate(zip(run_list, eventid_list)):
        #if run in run_completed_all or evtid in evtid_completed_all:
        #    continue

        print("\n")
        icecat_scan = False
        scan_list = skyscan.list_scans(int(run), int(evtid))
        df = pd.DataFrame(scan_list)
        progress = 0 

        for _, row in df.iterrows():
            if row['additional_tag'] == additional_tag:
                scan_id = row['id']
                reco_algo = row['reco_algo']
                time_scan = row['last_updated']
                progress = float(re.findall(pattern, row['progress'])[0]) * 100
                print(f"{i+1}) Run = {int(run)}, EventID = {int(evtid)}")
                print(f"scan_id = {scan_id} \n Last update = {time_scan} --> Progress of the scan with {reco_algo} = {progress:.1f}%")
                icecat_scan = True

        if not icecat_scan:
            print(f"{i+1}) Run = {int(run)}, EventID = {int(evtid)} --> No scans launched for IceCat")
            if outputfile and f1:
                f1.write(f"{run}\t{evtid}\n")

        if outputfile and icecat_scan:
            if progress == 100 and f2:
                f2.write(f"{run}\t{evtid}\t{reco_algo}\t{scan_id}\n")
            elif progress < 100 and f3:
                f3.write(f"{run}\t{evtid}\t{reco_algo}\t{scan_id}\t{progress}\n")

        time.sleep(10)

    if outputfile:
        if f1: f1.close()
        if f2: f2.close()
        if f3: f3.close()

def check_scans_completed(run_list, eventid_list, additional_tag):

    run_completed_all, evtid_completed_all = take_completed_scans()

    skyscan = SkyScan()
    pattern = r'\((-?\d+\.?\d*)\)'
    for i in range(len(run_list)):

        #print(run_list[i],eventid_list[i])

        if (run_list[i] in run_completed_all) and (eventid_list[i] in evtid_completed_all):
            #print('Already among the list of completed scans...')
            continue

        #print('Not in the list. Check its status ...')
        icecat_scan = False
        scan_list = skyscan.list_scans(int(run_list[i]),int(eventid_list[i]))
        df = pd.DataFrame(scan_list)
        for j in range(len(df)):
            if(df.iloc[j]['additional_tag']==additional_tag):
                scan_id   = df.iloc[j]['id']
                reco_algo = df.iloc[j]['reco_algo']
                time_scan = df.iloc[j]['last_updated']
                progress  = float(re.findall(pattern, df.iloc[j]['progress'])[0])*100
                icecat_scan = True
                print('Run = %i, EventID = %i' %(int(run_list[i]),int(eventid_list[i])))
                print('scan_id = %s \n Last update = %s --> Progress of the scan with %s = %.1f%%' %(scan_id,time_scan,reco_algo,progress))
            if(icecat_scan==True and int(progress)==100):
                print('Now completed!')
                print(int(run_list[i]),int(eventid_list[i]),reco_algo,scan_id)
        time.sleep(10)

def scan_runs(run_list, eventid_list):

    skyscan = SkyScan()
    for i in range(len(run_list)):
        print(int(run_list[i]),int(eventid_list[i]))
        scan_list = skyscan.list_scans(int(run_list[i]),int(eventid_list[i]))
        if scan_list.shape[0] > 0:
            formatted_list = skyscan.format_table(scan_list)
            print(formatted_list)

#infile = "evts_without_scan_28Jan.txt"
#run, eventid = np.loadtxt(infile, usecols=(0,1), unpack=True, dtype=int)
#check_progress_scan(run, eventid, 'icecat_test')
#check_progress_scan(run, eventid, 'icecat_test', outputfile=True)
#delete_scans(run, eventid, 'icecat_test')
#quit()

print(f'Checking old events (no I3Live) ...')
#infile = cfg.alerts_table_dir+"last_alerts.txt"
infile = cfg.alerts_table_dir+"alerts_no_i3live.txt"
run_no_i3live, eventid_no_i3live = np.loadtxt(infile, usecols=(0,1), unpack=True, dtype=int)
check_progress_scan(run_no_i3live, eventid_no_i3live, 'icecat_test', tag_file='_old_evts', outputfile=True)
#check_scans_completed(run_no_i3live, eventid_no_i3live, 'icecat_test')
#scan_runs(run_no_i3live, eventid_no_i3live)
#delete_scans(run_no_i3live, eventid_no_i3live, 'icecat_test')

print(f'Checking events on I3Live ...')
infile = cfg.alerts_table_dir+"alerts_i3live.txt"
#infile = cfg.alerts_table_dir+"last_scans.txt"
run_i3live, eventid_i3live = np.loadtxt(infile, usecols=(0,1), unpack=True, dtype=int)
#scan_runs(run_i3live, eventid_i3live)
check_progress_scan(run_i3live, eventid_i3live, 'icecat_test', tag_file='_i3live_evts', outputfile=True)
#check_scans_completed(run_i3live, eventid_i3live, 'icecat_test')
#delete_scans(run_i3live, eventid_i3live, 'icecat_test')
