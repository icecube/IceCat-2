from icecube.icetray import I3Tray, I3Units, I3Frame
import os
from os import listdir
from os.path import isfile, join

from icecube import (
    dataclasses,
    DomTools,
    frame_object_diff,
    gulliver,
    gulliver_modules,
    icetray,
    lilliput,
    mue,
    spline_reco,
    photonics_service,
    recclasses,
    simclasses,
    STTools,
    VHESelfVeto,
    dataio, 
    phys_services,  
    truncated_energy, 
)
from icecube.STTools.seededRT.configuration_services import I3DOMLinkSeededRTConfigurationService

import config
cfg = config.config()

def extract_baseline_file(run):
    
    gcd_folder = cfg.baseline_gcd_path

    # Get a list of all files in the folder with their full paths
    gcd_files = [os.path.join(gcd_folder, f) for f in os.listdir(gcd_folder) if os.path.isfile(os.path.join(gcd_folder, f))]
    # Sort files by their modification time
    gcd_files_sorted_by_time = sorted(gcd_files, key=os.path.getmtime)

    # Take the most updated baseline at run occurrence 
    for f in gcd_files_sorted_by_time:
        run_f = f[-9:-3]    # Take the run starting from which the baseline file was made available (from the filename itself)
        if(int(run_f)<run):
            gcd_file = f    

    return f

def add_truncated_energy_orig_i3file(run, eventid):

    input_file  = cfg.i3files_dir+'run'+str(run)+'_eventid'+str(eventid)+'.i3'
    output_file = cfg.i3files_dir+'run'+str(run)+'_eventid'+str(eventid)+'_v2.i3'

    gcd_file = extract_baseline_file(run)

    amplitudetable = cfg.splines_tables_path+"InfBareMu_mie_abs_z20a10_V2.fits"
    timingtable = cfg.splines_tables_path+"InfBareMu_mie_prob_z20a10_V2.fits"
    
    tray = I3Tray()
    tray.AddModule("I3Reader", "reader", FilenameList = [
        gcd_file,
        input_file
    ])
    seededRTConfig = I3DOMLinkSeededRTConfigurationService(
        # RT = Radius and Time
        ic_ic_RTRadius=150.0 * I3Units.m,
        ic_ic_RTTime=1000.0 * I3Units.ns,
        treat_string_36_as_deepcore=False,
        useDustlayerCorrection=False,
        allowSelfCoincidence=True,
    )

    tray.AddModule(
        "I3SeededRTCleaning_RecoPulseMask_Module",
        "BaseProc_RTCleaning",
        InputHitSeriesMapName="SplitInIcePulses",
        OutputHitSeriesMapName="SplitRTCleanedInIcePulses",
        STConfigService=seededRTConfig,
        SeedProcedure="HLCCoreHits",
        NHitsThreshold=2,
        MaxNIterations=3,
        Streams=[I3Frame.Physics],
    )

    tray.AddModule(
        "I3TimeWindowCleaning<I3RecoPulse>",
        "BaseProc_TimeWindowCleaning",
        InputResponse="SplitRTCleanedInIcePulses",
        OutputResponse="l2_online_CleanedMuonPulses",
        TimeWindow=6000 * I3Units.ns,
    )
    tray.Add(
        "I3PhotoSplineServiceFactory",
        "PhotonicsService",
        amplitudetable = amplitudetable,
        timingtable    = timingtable,
        timingSigma    = 0.0,
    )

    tray.AddModule(
        "I3TruncatedEnergy",
        "truncated_energy",
        RecoPulsesName="l2_online_CleanedMuonPulses",
        RecoParticleName="OnlineL2_SplineMPE",
        ResultParticleName="OnlineL2_SplineMPE_TruncatedEnergy",
        I3PhotonicsServiceName="PhotonicsService",
    )
    #RecoParticleName="l2_online_SplineMPE",
    #ResultParticleName="l2_online_SplineMPE_TruncatedEnergy",

    tray.AddModule(
        "I3Writer",
        "writer",
        Filename=output_file,
        streams=[icetray.I3Frame.Geometry, icetray.I3Frame.Calibration, icetray.I3Frame.DetectorStatus, icetray.I3Frame.DAQ, icetray.I3Frame.Physics]
    )

    tray.Execute()
    tray.Finish()

def load_frames(infile):
    frame_packet = []
    i3f = dataio.I3File(infile)
    while True:
       if not i3f.more():
          return frame_packet
       frame = i3f.pop_frame()
       frame_packet.append(frame)

def extract_truncated_energy_orig_from_i3file(infile):

    frame_packet = load_frames(cfg.i3files_dir+infile)
    for f in frame_packet:
        if f.Stop == icetray.I3Frame.Physics:
            te_orig = f["OnlineL2_SplineMPE_TruncatedEnergy_ORIG_Muon"].energy

    return te_orig
