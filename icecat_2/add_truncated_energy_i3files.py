from icecube.icetray import I3Tray, I3Units, I3Frame
import os
from os import listdir
from os.path import isfile, join
from icecube import (
    dataclasses,
    DomTools,
    frame_object_diff,
    #gulliver,
    #gulliver_modules,
    icetray,
    filter_tools,
    full_event_followup,
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
    trigger_splitter, ## added 
)
from icecube.STTools.seededRT.configuration_services import I3DOMLinkSeededRTConfigurationService
from icecube.common_variables import hit_statistics

from icecube.phys_services.which_split import which_split
from icecube.online_filterscripts.online_filters.HESE_filter import HESE_filter
from icecube.online_filterscripts.online_filters.OnlineL2_filter import online_l2_filter
from icecube.filterscripts.ehefilter import EHEFilter

import icecube.lilliput.segments 

from icecube.online_filterscripts.online_filters.OnlineL2_filter import L2Reco, NewL2AdvancedReco

import config
cfg = config.config()

def SelectOnlyIceCubePulses(frame, pulses):
    """Create a masked pulsemap which contains only IceCube DOMs."""
    """From online filters."""
    max_icecube_string = 78
    mask = dataclasses.I3RecoPulseSeriesMapMask(
        frame,
        pulses,
        lambda om, idx, pulse: om.string <= max_icecube_string
    )  # noqa: ARG005                                                                                                    
    frame[pulses + "IC"] = mask
    return True

def rename_BadDomsList(frame):
    if frame.Has("BadDomsList"):
        frame.Put(
            "L2BadDOMs",
            frame.Get("BadDomsList"),
            frame.Stop
        )

def add_fake_IceTop_pulses(frame):
    frame["HLCTankPulses"] = dataclasses.I3RecoPulseSeriesMap()
    frame["SLCTankPulses"] = dataclasses.I3RecoPulseSeriesMap()

def apply_updated_filters(run, eventid, tag=''):

    input_file  = cfg.i3files_dir+'run'+str(run)+'_eventid'+str(eventid)+'_'+tag+'.i3'
    output_file = cfg.i3files_dir+'run'+str(run)+'_eventid'+str(eventid)+'_'+tag+'_final.i3'

    tray = I3Tray()
    tray.AddModule("I3Reader", "reader", FilenameList = [
        input_file,
    ])

    '''
    l2name = "OnlineL2"
    tray.Add(
        online_l2_filter,
        l2name,
        pulses="CleanedInIcePulses",
        If=which_split("InIceSplit")
    )
    '''

    '''
    tray.AddModule('I3TriggerSplitter', 'BaseProc_InIceSplitter',
                   SubEventStreamName='InIceSplit',
                   #TrigHierName='QTriggerHierarchy',
                   TrigHierName='I3TriggerHierarchy',
                   # Note: taking the SuperDST pulses
                   TriggerConfigIDs = [1011,
                                       1006,
                                       1007,
                                       21001,
                                       33001],
                   InputResponses=['InIceDSTPulses'],
                   OutputResponses=['SplitUncleanedInIcePulses'],
                   WriteTimeWindow = True  # Needed for EHE
               )
    '''

    seededRTConfig = I3DOMLinkSeededRTConfigurationService(
        ic_ic_RTRadius=150.0 * I3Units.m,
        ic_ic_RTTime=1000.0 * I3Units.ns,
        treat_string_36_as_deepcore=False,
        useDustlayerCorrection=False,
        allowSelfCoincidence=True,
    )

    tray.AddModule(
        "I3SeededRTCleaning_RecoPulseMask_Module",
        "BaseProc_RTCleaning",
        #InputHitSeriesMapName="SplitUncleanedInIcePulses",
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
        OutputResponse="OnlineL2_CleanedMuonPulses",
        TimeWindow=6000 * I3Units.ns,
    )


    '''
    tray.Add(
        SelectOnlyIceCubePulses,
        "OnlineL2_SelectICPulses",
        pulses="OnlineL2_CleanedMuonPulses"
    )
    '''
    
    tray.Add(L2Reco, "OnlineL2", pulses="OnlineL2_CleanedMuonPulses",
             llhfit_name="PoleMuonLlhFit",
             linefit_name="PoleMuonLinefit",
             If=which_split("InIceSplit"))


    tray.Add(rename_BadDomsList)
    
    tray.Add(add_fake_IceTop_pulses) ## needed for NewL2AdvancedReco because inside that function it calculates also InTime IceTop hits (not needed for our purposes)

    # Add L2 advanced reconstructions for events that pass filter
    tray.Add(NewL2AdvancedReco,
             "OnlineL2",
             pulses="OnlineL2_CleanedMuonPulses",
             If=which_split("InIceSplit"))

    
    tray.Add(HESE_filter, "hese_online",
                 # Note HESE filter does not want cleaned pulses
                 pulses="SplitUncleanedInIcePulses",
                 If=which_split("InIceSplit"))
    tray.AddSegment(EHEFilter, "EHEFilter",
                 If = which_split("InIceSplit")
    )

    tray.AddModule(
        "I3Writer",
        "writer",
        Filename=output_file,
        streams=[icetray.I3Frame.Geometry, icetray.I3Frame.Calibration, icetray.I3Frame.DetectorStatus, icetray.I3Frame.DAQ, icetray.I3Frame.Physics]
    )

    tray.Execute()
    tray.Finish()


def add_truncated_energy_i3file(run, eventid, tag=''):

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
        #InputHitSeriesMapName="SplitUncleanedInIcePulses",
        InputHitSeriesMapName="InIceDSTPulses",
        OutputHitSeriesMapName="SplitRTCleanedInIcePulses",
        STConfigService=seededRTConfig,
        SeedProcedure="HLCCoreHits",
        NHitsThreshold=2,
        MaxNIterations=3,
        Streams=[I3Frame.Physics],
    )

    
    #if run>cfg.run_before_processing_update:
        
    tray.AddModule(
        "I3TimeWindowCleaning<I3RecoPulse>",
        "BaseProc_TimeWindowCleaning",
        InputResponse="SplitRTCleanedInIcePulses",
        OutputResponse="OnlineL2_CleanedMuonPulses",
        TimeWindow=6000 * I3Units.ns,
    )
    
    #else:
    
    tray.Add(
        SelectOnlyIceCubePulses,
        "OnlineL2_SelectICPulses",
        pulses="OnlineL2_CleanedMuonPulses"
    )
    
    tray.Add(
        hit_statistics.I3HitStatisticsCalculatorSegment,
        'OnlineL2_HitStatisticsValuesIC',
        PulseSeriesMapName='OnlineL2_CleanedMuonPulsesIC',
        OutputI3HitStatisticsValuesName='OnlineL2_HitStatisticsValuesIC',
        BookIt=True,
        #If=lambda f: If(f),
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
        RecoPulsesName="OnlineL2_CleanedMuonPulses",
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

def extract_truncated_energy_orig_muon_from_i3file(infile):

    frame_packet = load_frames(cfg.i3files_dir+infile)
    for f in frame_packet:
        if f.Stop == icetray.I3Frame.Physics:
            te_orig = f["OnlineL2_SplineMPE_TruncatedEnergy_ORIG_Muon"].energy

    return te_orig


#apply_updated_filters(131602,39194539,'i3live_pass2')
