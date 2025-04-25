import os
from pathlib import Path

class config:

    baseline_gcd_path   = '/data/user/followup/baseline_gcds/'
    splines_tables_path = '/cvmfs/icecube.opensciencegrid.org/data/photon-tables/splines/'

    gcd_folders_l2p2b = "/data/ana/IceCube/20*/filtered/level2pass2b/GCD/"
    run_folders_l2p2a = "/data/exp/IceCube/20*/filtered/level2pass2a/*/"
    run_folders_l2 = "/data/exp/IceCube/20*/filtered/level2/*/"

    ##########################################################################
    ## This part needed for the "old" way to process i3 file (before Tianlu's script for GDG pass2)
    old_alerts_path = '/data/ana/realtime/alert_catalog_v2/i3_files/'
    old_alerts_path_exception = '/data/ana/realtime/alert_catalog_v2/input_files/'
    new_alerts_path = '/data/ana/realtime/alert_catalog_v3/'
    ## 1st exception: another folder to be used and subevent 1 to be used !!!
    run_exception   = 123986 
    event_exception = 77999595
    ## 2nd exception: different namefile in the folder    
    run_exception_double_event   = 118973
    event_exception_double_event = 25391094
    ## 3rd exception: strange reco
    run_exception_strange_reco = 130684
    event_exception_strange_reco = 80612787
    ##########################################################################

    run_before_processing_update = 138599

    run_vetoed   = [118973, 120309, 121840, 122973, 126703, 130220, 131321, 133644]
    evtid_vetoed = [25391094, 20451977, 62872761, 6578595, 23477554, 11599241, 73241305, 43767651]
    
    te_orig_threshold   = 50000 ## GeV

    workdir = str(Path.cwd().parent)
    
    alerts_table_dir    = workdir+'/docs/'
    i3files_dir         = workdir+'/output/'

    # Create the folder if it doesn't exist
    if not os.path.exists(i3files_dir):
        os.makedirs(i3files_dir)

    key_passedfilters = 'AlertNamesPassed_IceCat2'

    possible_keys = [
        'AlertShortFollowupMsg',
        'BadDomsList',
        'BadDomsListSLC',
        'CalibratedWaveforms',
        'CalibratedWaveformRange',
        'CalibrationErrata',
        'CleanedMuonPulsesIC',
        'DSTTriggers',
        'Estres_CausalQTot',
        'Estres_HomogenizedQTot',
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
        'OnlineL2_CleanedMuonPulsesIC',
        'OnlineL2_HitStatisticsValuesIC',
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
        key_passedfilters
    ]

    fits_icecat1 = "/data/user/azegarelli/IceCat-2-fits-file-icecat1/docs/IceCat-1-dataverse_files/fits/"
    runs_icecat1_millipede_wilks   = [137668, 138181, 135908, 136260, 137467]
    events_icecat1_millipede_wilks = [51133257, 66037171, 43512334, 4895987, 64735045]

