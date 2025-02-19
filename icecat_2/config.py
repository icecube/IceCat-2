import os
from pathlib import Path

class config:

    baseline_gcd_path   = '/data/user/followup/baseline_gcds/'
    splines_tables_path = '/cvmfs/icecube.opensciencegrid.org/data/photon-tables/splines/'
    old_alerts_path = '/data/ana/realtime/alert_catalog_v2/i3_files/'
    old_alerts_path_exception = '/data/ana/realtime/alert_catalog_v2/input_files/'
    new_alerts_path = '/data/ana/realtime/alert_catalog_v3/'
    gcd_folders_l2p2b = "/data/ana/IceCube/20*/filtered/level2pass2b/GCD/"
    run_folders_l2p2a = "/data/exp/IceCube/20*/filtered/level2pass2a/*/"
    run_folders_l2 = "/data/exp/IceCube/20*/filtered/level2/*/"

    ## 1st exception: another folder to be used and subevent 1 to be used !!!
    run_exception   = 123986 
    event_exception = 77999595

    ## 2nd exception: different namefile in the folder    
    run_exception_double_event   = 118973
    event_exception_double_event = 25391094

    ## 3rd exception: strange reco
    run_exception_strange_reco = 130684
    event_exception_strange_reco = 80612787
    
    te_orig_threshold   = 50000 ## GeV

    workdir = str(Path.cwd().parent)
    
    alerts_table_dir    = workdir+'/docs/'
    i3files_dir         = workdir+'/output/'
    #i3files_dir = '/data/user/gsommani/IceCat-2/output/'
    # Create the folder if it doesn't exist
    if not os.path.exists(i3files_dir):
        os.makedirs(i3files_dir)

    possible_keys = [
        'AlertShortFollowupMsg',
        'BadDomsList',
        'BadDomsListSLC',
        'CalibratedWaveforms',
        'CalibratedWaveformRange',
        'CalibrationErrata',
        'DSTTriggers',
        'GoodRunEndTime',
        'GoodRunStartTime',
        'HESE_CausalQTot',
        'HESE_HomogenizedQTot',
        'HESE_VHESelfVeto',
        'HESE_VHESelfVetoVertexPos',
        'HESE_VHESelfVetoVertexTime',
        'I3Calibration',
        'I3DetectorStatus',
        'I3EventHeader',
        'I3Geometry',
        'I3SuperDST',
        'I3SuperDSTUnChargeCorrected',
        'InIceDSTPulses',
        'InIceRawData',
        'OnlineL2_BestFit',
        'OnlineL2_BestFit_CramerRao_cr_azimuth',
        'OnlineL2_BestFit_CramerRao_cr_zenith',
        'OnlineL2_SplineMPE',
        'OnlineL2_SplineMPEFitParams',
        'OnlineL2_SplineMPE_Bootstrap_Angular',
        'OnlineL2_SplineMPE_Characteristics',
        'OnlineL2_SplineMPE_CramerRao_cr_azimuth',
        'OnlineL2_SplineMPE_CramerRao_cr_zenith',
        'PoleEHESummaryPulseInfo',
        'SaturationWindows',
        'SplitUncleanedInIcePulses',
        'SplitUncleanedInIcePulsesTimeRange',
        'Streams'
    ]

    fits_icecat1 = "/data/user/azegarelli/IceCat-2-fits-file-icecat1/docs/IceCat-1-dataverse_files/fits/"
    runs_icecat1_millipede_wilks   = [137668, 138181, 135908, 136260, 137467]
    events_icecat1_millipede_wilks = [51133257, 66037171, 43512334, 4895987, 64735045]

