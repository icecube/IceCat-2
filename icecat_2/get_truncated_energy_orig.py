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

def add_truncated_energy_orig_i3file(run, eventid, tag=''):

    input_file  = cfg.i3files_dir+'run'+str(run)+'_eventid'+str(eventid)+'_'+tag+'.i3'
    output_file = cfg.i3files_dir+'run'+str(run)+'_eventid'+str(eventid)+'_'+tag+'_te.i3'

    amplitudetable = cfg.splines_tables_path+"InfBareMu_mie_abs_z20a10_V2.fits"
    timingtable = cfg.splines_tables_path+"InfBareMu_mie_prob_z20a10_V2.fits"
    
    tray = I3Tray()
    tray.AddModule("I3Reader", "reader", FilenameList = [
        input_file,
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
        #InputHitSeriesMapName="SplitInIcePulses",
        InputHitSeriesMapName="InIceDSTPulses",
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
