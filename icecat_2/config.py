import os

class config:

    baseline_gcd_path   = '/data/user/followup/baseline_gcds/'
    splines_tables_path = '/cvmfs/icecube.opensciencegrid.org/data/photon-tables/splines/'
    old_alerts_path = '/data/ana/realtime/alert_catalog_v2/i3_files/'

    te_orig_threshold   = 50000 ## GeV

    workdir             = '/home/gsommani/IceCat-2/'

    alerts_table_dir    = workdir+'/docs/'
    i3files_dir         = workdir+'output/'
    # Create the folder if it doesn't exist
    if not os.path.exists(i3files_dir):
        os.makedirs(i3files_dir)

    possible_keys = [
        'AlertShortFollowupMsg',
        'DSTTriggers',
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
        'InIceDSTPulses',
        'OnlineL2_BestFit',
        'OnlineL2_SplineMPE',
        'OnlineL2_SplineMPEFitParams',
        'OnlineL2_SplineMPE_Bootstrap_Angular',
        'OnlineL2_SplineMPE_Characteristics',
        'OnlineL2_SplineMPE_CramerRao_cr_azimuth',
        'OnlineL2_SplineMPE_CramerRao_cr_zenith',
        'SplitInIcePulses',
        'SplitInIcePulsesTimeRange',
        'Streams'
    ]
